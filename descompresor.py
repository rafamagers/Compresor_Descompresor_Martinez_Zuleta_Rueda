import time
import sys
###############################################################################################
##                                 Descompresor Mágico                                       ##
###############################################################################################
start_time = time.time()
def byte_to_binary(byte):
    # Convierte el byte en un número entero utilizando la función int.from_bytes()
    num = int.from_bytes(byte, byteorder='big')
    
    # Convierte el número en una cadena binaria utilizando la función bin()
    binary_str = bin(num)[2:]
    
    # Rellena la cadena binaria con ceros a la izquierda si es necesario
    padding = '0' * (8 - len(binary_str))
    binary_str = padding + binary_str  
    return binary_str
Lines = []
for line in open(sys.argv[1], 'rb').readlines():
  Lines.append(line)
my_string=[]
for h in Lines:
  for t in h:
    my_string.append(t.to_bytes((t.bit_length() + 7) // 8, byteorder='big'))
re = []
for cont in range(len(my_string)):
  if (cont>3):
    if(my_string[cont]==b"%"and my_string[cont-1]==b"@" and my_string[cont-2]==b"%"):
      re = []
    else:
      re.append(my_string[cont])
cad = []
for h in re:
  cad.append(byte_to_binary(h))
cad = "".join(cad)
for i in range(8):
  if cad[0] == "0":
    cad = cad[1:]
  else:
    break           
a=b"".join(my_string)
linea = a.split(b"%@%")
letter_binary2 = {}
i=0
while i < len(linea)-2:
  codbin = linea[i+1].decode()
  letter_binary2[codbin]=linea[i]
  i=i+2
uncompressed_string = []
packsize = 40000
cadenita = b""
cadena_binaria = linea[len(linea)-2].decode() + cad
digit_bit = ""
for digit in cadena_binaria:
  digit_bit = digit_bit + digit
  if(digit_bit in letter_binary2):
    cadenita = cadenita + letter_binary2[digit_bit]    
    digit_bit = ""
  if (len(cadenita)>packsize):
    uncompressed_string.append(cadenita)
    cadenita = b""
code=b"".join(uncompressed_string)
# Se guarda el archivo en la ubicación especificada
with open("descomprimido-elmejorprofesor.txt", "wb") as f:
    f.write(code)
# Indicadores
end_time = time.time()
tiempo_ejecucion = end_time - start_time
tiempo_ejecucion_r = round(tiempo_ejecucion, 2)
print(tiempo_ejecucion_r)