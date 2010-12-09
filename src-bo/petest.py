import pefile

pe = pefile.PE('launcher.exe')
print pe.OPTIONAL_HEADER.AddressOfEntryPoint
print pe.OPTIONAL_HEADER.ImageBase
print pe.FILE_HEADER.NumberOfSections

for section in pe.sections:
    print (section.Name, hex(section.VirtualAddress),
           hex(section.Misc_VirtualSize), section.SizeOfRawData )

for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print entry.dll
    for imp in entry.imports:
        print '\t', hex(imp.address), imp.name

print "--------------------------------------"
print pe.dump_info()

#ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
#ep_ava = ep+pe.OPTIONAL_HEADER.ImageBase
#data = pe.get_memory_mapped_image()[ep:ep+100]
#offset = 0
#while offset < len(data):
#  i = pydasm.get_instruction(data[offset:], pydasm.MODE_32)
#  print pydasm.get_instruction_string(i, pydasm.FORMAT_INTEL, ep_ava+offset)
#  offset += i.length
