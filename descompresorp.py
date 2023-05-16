from mpi4py import MPI
import sys
import time
start = time.time()
def primeCheck(num):
    divisores = 0
    for ii in range(2, num):
        if num % ii == 0:
            divisores += 1
            break
    if divisores == 0:  
        return True
    else:
        return False

comm = MPI.COMM_WORLD  # Comunicador entre procesos
import time
from mpi4py import MPI
###############################################################################################
##                                 Descompresor Mágico                                       ##
###############################################################################################
start_time = time.time()
comm = MPI.COMM_WORLD  # Comunicador entre procesos
rank = comm.Get_rank()  # Identificador del proceso actual
size = comm.Get_size() # Número total de procesos
if rank == 0:
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
  print("leyendo")
  for line in open("comprimido.elmejorprofesor", 'rb').readlines():
    Lines.append(line)
  my_string=[]
  print("terminar leer")

  print("Traducir a bytes")
  for h in Lines:
    for t in h:
      my_string.append(t.to_bytes((t.bit_length() + 7) // 8, byteorder='big'))
  re = []
  print("terminada traduccion")

  print("Construir cadena a traducir")
  for cont in range(len(my_string)):
    if (cont>3):
      if(my_string[cont]==b"%"and my_string[cont-1]==b"@" and my_string[cont-2]==b"%"):
        re = []
      else:
        re.append(my_string[cont])
  print("cadena terminada")
  cad = []
  print("converitr cadena a binaria")
  for h in re:
    cad.append(byte_to_binary(h))
  cad = "".join(cad)
  print("binario terminado")
  for i in range(8):
    if cad[0] == "0":
      cad = cad[1:]
    else:
      break           
  print("Contruir diccionario")
  a=b"".join(my_string)
  linea = a.split(b"%@%")
  letter_binary2 = {}
  i=0
  while i < len(linea)-2:
    codbin = linea[i+1].decode()
    letter_binary2[codbin]=linea[i]
    i=i+2
  print(letter_binary2)
  print("Dicionario construido")
  cadena_binaria = linea[len(linea)-2].decode() + cad
  for h in range(size):
    cadena_nodo = cadena_binaria[h*len(cadena_binaria)//size:(h+1)*len(cadena_binaria)//size ]
    if h!=0:
       comm.send([cadena_nodo,rank,letter_binary2],dest=h)
    else:
       cadi = cadena_nodo
digit_bit = ""
cadenita = b""
uncompressed_string = []
packsize = 40000
if (rank !=0):
   recibido = comm.recv(source=0)
   cadi = recibido[0]
   letter_binary2 = recibido[2]
print(len(cadi))
for digit in cadi:
  digit_bit = digit_bit + digit
  if(digit_bit in letter_binary2):
    cadenita = cadenita + letter_binary2[digit_bit]    
    digit_bit = ""
  if (len(cadenita)>packsize/size):
    uncompressed_string.append(cadenita)
    cadenita = b""
if (rank!=0):
   comm.send([uncompressed_string,rank],dest=0)
else:
  print("falto yo")
  code = b"".join(uncompressed_string)
  for h in range(size):
    if (h!=0):    
      aux = comm.recv(source=h)
      code = code + b"".join(aux[0])
  # Se guarda el archivo en la ubicación especificada
  with open("descomprimido-elmejorprofesor.txt", "wb") as f:
      f.write(code)
  # Indicadores
  print("Archivo descomprimido exitosamente")
  end_time = time.time()
  tiempo_ejecucion = end_time - start_time
  tiempo_ejecucion_r = round(tiempo_ejecucion, 2)
  print("El tiempo de ejecución fue:",tiempo_ejecucion_r,"segundos")