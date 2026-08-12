# Simple Minecraft brarchive compiler!

This system will compile your addon into optimized packs (`.brarchive`) and automatically generate a `.mcaddon` or `.mcpack` file.

## How to use

1. Place your files inside the `/src` folder, in the corresponding folders:
   - `BP` for your Behavior Pack files
   - `RP` for your Resource Pack files

2. Set up the Bedrock Server executable:
   - Download the official Bedrock dedicated server from [minecraft.net/pt-br/download/server/bedrock](https://www.minecraft.net/pt-br/download/server/bedrock)
   - Extract the downloaded files.
   - Move **ONLY** the `bedrock_server.exe` file into the `bedrock_server/` folder.

3. Run the `brarchive-compiler.py` script:
   - Through the terminal: `python brarchive-compiler.py`
   - Or simply double-click `execute.cmd`

4. During execution, choose a name for the generated file.

5. Your generated files will be in `/dist`!

## Dependencies

- **Python** (3.6 or higher)

## Credits

Created by Italo Amorim  
GitHub: https://github.com/iamorimm
Instagram: [@iamorim_](https://instagram.com/iamorim_)