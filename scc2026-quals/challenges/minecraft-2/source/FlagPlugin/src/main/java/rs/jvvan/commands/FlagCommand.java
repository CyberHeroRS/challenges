package rs.jvvan.commands;

import com.hypixel.hytale.component.Ref;
import com.hypixel.hytale.component.Store;
import com.hypixel.hytale.math.util.ChunkUtil;
import com.hypixel.hytale.math.vector.Vector3i;
import com.hypixel.hytale.server.core.Message;
import com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType;
import com.hypixel.hytale.server.core.command.system.CommandContext;
import com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg;
import com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes;
import com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand;
import com.hypixel.hytale.server.core.modules.entity.component.HeadRotation;
import com.hypixel.hytale.server.core.modules.entity.component.TransformComponent;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.world.SetBlockSettings;
import com.hypixel.hytale.server.core.universe.world.World;
import com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ThreadLocalRandom;
import java.util.logging.Level;

public class FlagCommand extends AbstractPlayerCommand {

    private static final String[] WOOL_BLOCK_IDS = {
            "Cloth_Block_Wool_Black",
            "Cloth_Block_Wool_Blue",
            "Cloth_Block_Wool_Blue_Light",
            "Cloth_Block_Wool_Cyan",
            "Cloth_Block_Wool_Cyan_Light",
            "Cloth_Block_Wool_Gray",
            "Cloth_Block_Wool_Gray_Light",
            "Cloth_Block_Wool_Green",
            "Cloth_Block_Wool_Green_Light",
            "Cloth_Block_Wool_Orange",
            "Cloth_Block_Wool_Orange_Light",
            "Cloth_Block_Wool_Pink",
            "Cloth_Block_Wool_Pink_Light",
            "Cloth_Block_Wool_Purple",
            "Cloth_Block_Wool_Purple_Light",
            "Cloth_Block_Wool_Red",
            "Cloth_Block_Wool_Red_Light",
            "Cloth_Block_Wool_White",
            "Cloth_Block_Wool_Yellow",
            "Cloth_Block_Wool_Yellow_Light"
    };

    // 5x7 glyphs scaled by 5 blocks per pixel gives letters around 25x35 blocks.
    private static final int PIXEL_SCALE = 5;
    private static final int LETTER_SPACING = PIXEL_SCALE;
    private static final int DRAW_DISTANCE = 6;
    private static final int BASE_Y_OFFSET = 1;
    private static final int BLOCK_SET_FLAGS =
            SetBlockSettings.NO_SEND_PARTICLES
                    | SetBlockSettings.FORCE_CHANGED
                    | SetBlockSettings.NO_UPDATE_NEIGHBOR_CONNECTIONS;

    private static final Map<Character, Glyph> GLYPHS = createGlyphs();

    private final RequiredArg<List<String>> textArg;

    public FlagCommand(String name, String description) {
        super(name, description);
        this.textArg = this.withListRequiredArg("text", "Text to draw", ArgTypes.STRING);
    }

    @Override
    protected void execute(
            CommandContext context,
            Store<EntityStore> entityStore,
            Ref<EntityStore> playerEntityRef,
            PlayerRef player,
            World world
    ) {
        String text = normalizeInput(this.textArg.get(context));
        if (text.isEmpty()) {
            player.sendMessage(Message.raw("Usage: /flag <text>").color("#D64040"));
            return;
        }

        List<BlockType> woolPalette = resolveWoolPalette();
        if (woolPalette.isEmpty()) {
            player.sendMessage(Message.raw("No wool block types could be resolved.").color("#D64040"));
            return;
        }

        TransformComponent transform = entityStore.getComponent(playerEntityRef, TransformComponent.getComponentType());
        HeadRotation headRotation = entityStore.getComponent(playerEntityRef, HeadRotation.getComponentType());
        if (transform == null || headRotation == null) {
            player.sendMessage(Message.raw("Could not read your position to draw the text.").color("#D64040"));
            return;
        }

        Vector3i playerPosition = transform.getPosition().clone().floor().toVector3i();
        Vector3i forward = headRotation.getHorizontalAxisDirection();
        if (forward.x == 0 && forward.z == 0) {
            forward = new Vector3i(0, 0, -1);
        }

        List<PlacedBlock> blocks = buildBlocks(text, playerPosition, forward, woolPalette);
        if (blocks.isEmpty()) {
            player.sendMessage(Message.raw("Nothing to draw for that text.").color("#D64040"));
            return;
        }

        Map<Long, CompletableFuture<WorldChunk>> chunkFutures = new LinkedHashMap<>();
        for (PlacedBlock block : blocks) {
            chunkFutures.computeIfAbsent(block.chunkIndex, world::getChunkAsync);
        }

        CompletableFuture
                .allOf(chunkFutures.values().toArray(new CompletableFuture[0]))
                .thenRunAsync(() -> placeBlocks(player, text, blocks, chunkFutures), world)
                .exceptionally(error -> {
                    LOGGER.at(Level.SEVERE).withCause(error).log("Failed to draw /flag text");
                    world.execute(() -> player.sendMessage(Message.raw("Failed to draw the text. Check the server log.").color("#D64040")));
                    return null;
                });
    }

    private void placeBlocks(
            PlayerRef player,
            String text,
            List<PlacedBlock> blocks,
            Map<Long, CompletableFuture<WorldChunk>> chunkFutures
    ) {
        Map<Long, WorldChunk> loadedChunks = new HashMap<>(chunkFutures.size());
        for (Map.Entry<Long, CompletableFuture<WorldChunk>> entry : chunkFutures.entrySet()) {
            loadedChunks.put(entry.getKey(), entry.getValue().join());
        }

        int placedCount = 0;
        for (PlacedBlock block : blocks) {
            WorldChunk chunk = loadedChunks.get(block.chunkIndex);
            if (chunk != null && chunk.setBlock(block.x, block.y, block.z, block.blockType, BLOCK_SET_FLAGS)) {
                placedCount++;
            }
        }

        player.sendMessage(
                Message.raw("Drew \"" + text + "\" with " + placedCount + " random wool blocks.")
                        .color("#FFFFFF")
        );
    }

    private List<PlacedBlock> buildBlocks(String text, Vector3i playerPosition, Vector3i forward, List<BlockType> woolPalette) {
        Vector3i right = new Vector3i(-forward.z, 0, forward.x);
        int totalWidth = measureTextWidth(text);
        int startX = playerPosition.x + (forward.x * DRAW_DISTANCE) - (right.x * (totalWidth / 2));
        int startY = playerPosition.y + BASE_Y_OFFSET;
        int startZ = playerPosition.z + (forward.z * DRAW_DISTANCE) - (right.z * (totalWidth / 2));

        List<PlacedBlock> blocks = new ArrayList<>();
        int cursor = 0;
        for (int index = 0; index < text.length(); index++) {
            Glyph glyph = resolveGlyph(text.charAt(index));

            for (int row = 0; row < glyph.rows.length; row++) {
                String rowPattern = glyph.rows[row];
                for (int col = 0; col < rowPattern.length(); col++) {
                    if (rowPattern.charAt(col) != '1') {
                        continue;
                    }

                    int pixelX = startX + (right.x * (cursor + (col * PIXEL_SCALE)));
                    int pixelY = startY + ((glyph.rows.length - 1 - row) * PIXEL_SCALE);
                    int pixelZ = startZ + (right.z * (cursor + (col * PIXEL_SCALE)));
                    addScaledPixel(blocks, pixelX, pixelY, pixelZ, right, pickRandomWool(woolPalette));
                }
            }

            cursor += glyph.width * PIXEL_SCALE;
            if (index < text.length() - 1) {
                cursor += LETTER_SPACING;
            }
        }

        return blocks;
    }

    private void addScaledPixel(List<PlacedBlock> blocks, int baseX, int baseY, int baseZ, Vector3i right, BlockType blockType) {
        for (int offsetX = 0; offsetX < PIXEL_SCALE; offsetX++) {
            int blockX = baseX + (right.x * offsetX);
            int blockZ = baseZ + (right.z * offsetX);
            for (int offsetY = 0; offsetY < PIXEL_SCALE; offsetY++) {
                blocks.add(new PlacedBlock(blockX, baseY + offsetY, blockZ, blockType));
            }
        }
    }

    private int measureTextWidth(String text) {
        int width = 0;
        for (int index = 0; index < text.length(); index++) {
            width += resolveGlyph(text.charAt(index)).width * PIXEL_SCALE;
            if (index < text.length() - 1) {
                width += LETTER_SPACING;
            }
        }
        return width;
    }

    private Glyph resolveGlyph(char value) {
        char normalized = Character.isLetter(value) ? Character.toUpperCase(value) : value;
        return GLYPHS.getOrDefault(normalized, GLYPHS.get('?'));
    }

    private String normalizeInput(List<String> words) {
        StringBuilder builder = new StringBuilder();
        for (String word : words) {
            String trimmed = word == null ? "" : word.trim();
            if (trimmed.isEmpty()) {
                continue;
            }

            if (builder.length() > 0) {
                builder.append(' ');
            }
            builder.append(trimmed);
        }
        return builder.toString();
    }

    private List<BlockType> resolveWoolPalette() {
        List<BlockType> woolPalette = new ArrayList<>(WOOL_BLOCK_IDS.length);
        for (String blockId : WOOL_BLOCK_IDS) {
            BlockType blockType = BlockType.fromString(blockId);
            if (blockType != null && !blockType.isUnknown()) {
                woolPalette.add(blockType);
            }
        }
        return woolPalette;
    }

    private BlockType pickRandomWool(List<BlockType> woolPalette) {
        return woolPalette.get(ThreadLocalRandom.current().nextInt(woolPalette.size()));
    }

    private static Map<Character, Glyph> createGlyphs() {
        Map<Character, Glyph> glyphs = new HashMap<>();
        put(glyphs, 'A', "01110", "10001", "10001", "11111", "10001", "10001", "10001");
        put(glyphs, 'B', "11110", "10001", "10001", "11110", "10001", "10001", "11110");
        put(glyphs, 'C', "01111", "10000", "10000", "10000", "10000", "10000", "01111");
        put(glyphs, 'D', "11110", "10001", "10001", "10001", "10001", "10001", "11110");
        put(glyphs, 'E', "11111", "10000", "10000", "11110", "10000", "10000", "11111");
        put(glyphs, 'F', "11111", "10000", "10000", "11110", "10000", "10000", "10000");
        put(glyphs, 'G', "01110", "10001", "10000", "10111", "10001", "10001", "01110");
        put(glyphs, 'H', "10001", "10001", "10001", "11111", "10001", "10001", "10001");
        put(glyphs, 'I', "11111", "00100", "00100", "00100", "00100", "00100", "11111");
        put(glyphs, 'J', "00001", "00001", "00001", "00001", "10001", "10001", "01110");
        put(glyphs, 'K', "10001", "10010", "10100", "11000", "10100", "10010", "10001");
        put(glyphs, 'L', "10000", "10000", "10000", "10000", "10000", "10000", "11111");
        put(glyphs, 'M', "10001", "11011", "10101", "10001", "10001", "10001", "10001");
        put(glyphs, 'N', "10001", "11001", "10101", "10011", "10001", "10001", "10001");
        put(glyphs, 'O', "01110", "10001", "10001", "10001", "10001", "10001", "01110");
        put(glyphs, 'P', "11110", "10001", "10001", "11110", "10000", "10000", "10000");
        put(glyphs, 'Q', "01110", "10001", "10001", "10001", "10101", "10010", "01101");
        put(glyphs, 'R', "11110", "10001", "10001", "11110", "10100", "10010", "10001");
        put(glyphs, 'S', "01111", "10000", "10000", "01110", "00001", "00001", "11110");
        put(glyphs, 'T', "11111", "00100", "00100", "00100", "00100", "00100", "00100");
        put(glyphs, 'U', "10001", "10001", "10001", "10001", "10001", "10001", "01110");
        put(glyphs, 'V', "10001", "10001", "10001", "10001", "10001", "01010", "00100");
        put(glyphs, 'W', "10001", "10001", "10001", "10001", "10101", "11011", "10001");
        put(glyphs, 'X', "10001", "10001", "01010", "00100", "01010", "10001", "10001");
        put(glyphs, 'Y', "10001", "10001", "01010", "00100", "00100", "00100", "00100");
        put(glyphs, 'Z', "11111", "00001", "00010", "00100", "01000", "10000", "11111");
        put(glyphs, '0', "01110", "10001", "10011", "10101", "11001", "10001", "01110");
        put(glyphs, '1', "00100", "01100", "00100", "00100", "00100", "00100", "01110");
        put(glyphs, '2', "01110", "10001", "00001", "00010", "00100", "01000", "11111");
        put(glyphs, '3', "11110", "00001", "00001", "01110", "00001", "00001", "11110");
        put(glyphs, '4', "00010", "00110", "01010", "10010", "11111", "00010", "00010");
        put(glyphs, '5', "11111", "10000", "10000", "11110", "00001", "00001", "11110");
        put(glyphs, '6', "01110", "10000", "10000", "11110", "10001", "10001", "01110");
        put(glyphs, '7', "11111", "00001", "00010", "00100", "01000", "01000", "01000");
        put(glyphs, '8', "01110", "10001", "10001", "01110", "10001", "10001", "01110");
        put(glyphs, '9', "01110", "10001", "10001", "01111", "00001", "00001", "01110");
        put(glyphs, '!', "00100", "00100", "00100", "00100", "00100", "00000", "00100");
        put(glyphs, '?', "01110", "10001", "00010", "00100", "00100", "00000", "00100");
        put(glyphs, '.', "00000", "00000", "00000", "00000", "00000", "00100", "00100");
        put(glyphs, '-', "00000", "00000", "00000", "11111", "00000", "00000", "00000");
        put(glyphs, '_', "00000", "00000", "00000", "00000", "00000", "00000", "11111");
        put(glyphs, '{', "00011", "00100", "00100", "11000", "00100", "00100", "00011");
        put(glyphs, '}', "11000", "00100", "00100", "00011", "00100", "00100", "11000");
        glyphs.put(' ', new Glyph(3, new String[]{"000", "000", "000", "000", "000", "000", "000"}));
        return glyphs;
    }

    private static void put(Map<Character, Glyph> glyphs, char character, String... rows) {
        glyphs.put(character, new Glyph(rows[0].length(), rows));
    }

    private static final class Glyph {
        private final int width;
        private final String[] rows;

        private Glyph(int width, String[] rows) {
            this.width = width;
            this.rows = rows;
        }
    }

    private static final class PlacedBlock {
        private final int x;
        private final int y;
        private final int z;
        private final BlockType blockType;
        private final long chunkIndex;

        private PlacedBlock(int x, int y, int z, BlockType blockType) {
            this.x = x;
            this.y = y;
            this.z = z;
            this.blockType = blockType;
            this.chunkIndex = ChunkUtil.indexChunkFromBlock(x, z);
        }
    }
}
