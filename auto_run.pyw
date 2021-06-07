import os

if os.path.exists('snip_and_sketch.exe'):
    os.system('snipping_tool.exe')
    os.remove('capture.png')

elif os.path.exists('snip_and_sketch.pyw'):
    os.system('snip_and_sketch.pyw')
    os.remove('capture.png')

else:
    print("""snipping_tool wasn't  installed correctly, to do it manually
Go to 'https://github.com/Pranav578/Snip_and_Sketch' and install either snipping_tool.pyw or snipping_tool.exe""")


