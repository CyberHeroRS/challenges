package rs.jvvan;

import com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent;
import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;
import rs.jvvan.commands.FlagCommand;

import javax.annotation.Nonnull;

public class FlagPlugin extends JavaPlugin {

    public FlagPlugin(@Nonnull JavaPluginInit init) {
        super(init);
    }

    @Override
    protected void setup() {
        this.getCommandRegistry().registerCommand(new FlagCommand("flag", "Draw a flag"));
    }
}