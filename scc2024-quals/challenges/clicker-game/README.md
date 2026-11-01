# ClickerGame

**Author**: Lazar Mancic / Jovan Pavlovic  
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: Someone told me that if i click enough times all seecrets of this world will be revealed
**Infrastructure requirements**: zip  

Flag: `SCC{1_h0p3_y0u_d1d_n07_cl1ck3d_7h15_0u7}`

# Solution

Players will have to decompile apk file to get encoded flag from resources, create small script to automate seeded random to get correct xor key and decrypt string.

```java
import java.util.Random;
 
public class Main {
    private static byte[] decodeHex(String hexString) {
        int len = hexString.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hexString.charAt(i), 16) << 4) + Character.digit(hexString.charAt(i + 1), 16));
        }
        return data;
    }


    public static void main(String[] args) {

        String flag = "60a0ecad9a56c73e779ce68b1a624e70923c7dbf02a2fdfce74090c36aa593abedb22d9c877a292c";

        Random rnd = new Random();
        rnd.setSeed(322419390L);

        for(int i = 0; i < 322419390L; i++)
        {
            rnd.nextInt();
        }

        byte[] data = decodeHex(flag);
        for (int i = 0; i < data.length; i++) {
            data[i] = (byte) (data[i] ^ (rnd.nextInt() & 255));
        }

        System.out.println(new String(data));
    }
}
```