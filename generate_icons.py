import base64

# Convert ICO file to base64
with open("ppm-ico.ico", "rb") as f:
    ico_data = base64.b64encode(f.read()).decode('utf-8')

# Convert PNG file to base64
with open("ppm-png.png", "rb") as f:
    png_data = base64.b64encode(f.read()).decode('utf-8')

# Write the output to a text file
with open("icons_base64.txt", "w") as f:
    f.write("PPM_ICO_BASE64 = '''\n")
    f.write(ico_data)
    f.write("'''\n\n")
    f.write("PPM_PNG_BASE64 = '''\n")
    f.write(png_data)
    f.write("'''\n")

print("Icons converted to base64 and saved in icons_base64.txt!")
