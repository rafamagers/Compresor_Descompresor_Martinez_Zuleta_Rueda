from mpi4py import MPI
import sys
import time
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
  for line in open("comprimido.elmejorprofesor", 'rb').readlines():
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
  letter_binary3 = {}
  i=0
  while i < len(linea)-2:
    codbin = linea[i+1].decode()
    letter_binary2[codbin]=linea[i]
    letter_binary3[linea[i]]=codbin
    i=i+2
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
for digit in cadi:
  digit_bit = digit_bit + digit
  if(digit_bit in letter_binary2):
    cadenita = cadenita + letter_binary2[digit_bit]    
    digit_bit = ""
  if (len(cadenita)>packsize/size):
    uncompressed_string.append(cadenita)
    cadenita = b""
uncompressed_string.append(cadenita)
if (rank!=0):
   comm.send([uncompressed_string,rank,digit_bit],dest=0)
else:
  sobrante = digit_bit
  code = b"".join(uncompressed_string)
  for h in range(size):
    if (h!=0):    
      aux = comm.recv(source=h)
      codigo = b"".join(aux[0])
      acorregir = codigo[0:20]
      byte = b""
      cadenabin = ""
      for jj in acorregir:
        y = jj.to_bytes((t.bit_length() + 7) // 8, byteorder='big')
        byte = byte+y
        if byte in letter_binary3:
          cadenabin = cadenabin+letter_binary3[byte]
          byte = b""
      newbinary = sobrante +cadenabin
      sobrante = aux[2]
      digit_bit=""
      cadenit = b""
      for digit in newbinary:
        digit_bit = digit_bit + digit
        if(digit_bit in letter_binary2):
          cadenit = cadenit + letter_binary2[digit_bit]    
          digit_bit = ""
      code = code+cadenit+codigo[20:len(codigo)]
  # Se guarda el archivo en la ubicación especificada
  with open("descomprimido-elmejorprofesor.txt", "wb") as f:
      f.write(code)
  # Indicadores
  end_time = time.time()
  tiempo_ejecucion = end_time - start_time
  tiempo_ejecucion_r = round(tiempo_ejecucion, 2)
  print("El tiempo de ejecución fue:",tiempo_ejecucion_r,"segundos")