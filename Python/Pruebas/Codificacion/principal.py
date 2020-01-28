#!/usr/bin/python3
import base64
import qrcode
from CRC16 import CRC16
from confTeclado import confTeclado

class codificar():
    def __init__(self):
        pass

    def codeInfoQR(self, informacion):        
        infoInBytes = bytes( informacion, 'utf-8')
        print(infoInBytes, file=open("InfoInBytes.txt", "a"))
        encoded = base64.b64encode(infoInBytes)
        print(encoded, file=open("InfoCoded.txt", "a"))
        return encoded

    def generarQR(self, infoCoded, expedidoraID, folio ):
        qr = qrcode.make(infoCoded)
        nombre = 'QR_' + str(expedidoraID)+ '_' + str(folio) + '.png' 
        qr.save( nombre )
        print(nombre, file=open("QRFiles.txt", "a"))
        return nombre

    def cleanCharQR( self, ticketQR ):
        limpiaAdmiracion = ticketQR.replace( '¿', '+' )
        limpiaComillas = limpiaAdmiracion.replace( "'", '-' )
        limpiaInterrogacion = limpiaComillas.replace( '¡', '=' )
        ticketQRFinal = limpiaInterrogacion
        print(ticketQRFinal, file=open("infoRead.txt", "a"))
        return ticketQRFinal

    def decodeInfoQR(self, informacion):
        decoded = base64.b64decode(informacion)
        infoInString = str( decoded, 'utf-8')
        print(infoInString, file=open("infoReadCoded.txt", "a"))
        return infoInString

    def validarExist(self, infoIni, infoFin):
        if infoIni == infoFin:
            return True
        else:
            return False
    def validarCR7s(self, CR7, CR72):
        if CR7 == CR72:
            return True
        else:
            return False

    def calcularCR7(self, inFormacion):
        strInformacion = str( inFormacion, 'utf-8')
        CR7 = CRC16().calculate(strInformacion)
        return str(CR7)

    def procesamiento(self,informacion):
        infoTotal = informacion.split(',')
        ticketQRLimpio = self.cleanCharQR( infoTotal[0] )
        CRC2 = self.calcularCR7(bytes(ticketQRLimpio, 'utf-8'))
        ticketDecodificado = self.decodeInfoQR(ticketQRLimpio)
        if(self.validarCR7s(infoTotal[1], CRC2)):
            return ticketDecodificado
        else:
            return False

def main():
    codificador = codificar()
    read = str(input("Ingrese ticket QR:"))
    resultado = codificador.procesamiento(read)
    print(resultado)


if __name__ == "__main__":
    main()
