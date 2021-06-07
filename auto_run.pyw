import os

if os.path.exists('snip_and_sketch.pyw'):
    os.system('snip_and_sketch.pyw')
    os.remove('capture.png')

else:
    print("""snipping_tool wasn't  installed correctly, to do it manually
Go to 'https://github.com/Pranav578/Snip_and_Sketch' and install snipping_tool.pyw""")
