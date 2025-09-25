from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import Response, FileResponse
from schemas.accion import AccionRequest, AccionResponse, AccionUpdateRequest, AccionResponseCompleta, DescifrarCertificadoRequest, StripePaymentRequest, StripePaymentResponse, StripeWebhookResponse, MercadoPagoPaymentRequest, MercadoPagoPaymentResponse, MercadoPagoWebhookResponse, PayPalPaymentRequest, PayPalPaymentResponse, PayPalExecuteRequest
from use_cases.accion import AccionUseCase
from infrastructure.accion_repository import AccionRepository
from infrastructure.qr_service import QRService
from infrastructure.certificate_service import CertificateService
from infrastructure.temp_payment_service import TempPaymentService
from infrastructure.stripe_service import StripeService
from infrastructure.mercadopago_service import MercadoPagoService
from infrastructure.paypal_service import PayPalService
from infrastructure.socio_repository import SocioRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
import base64
import json
import os
import logging
from datetime import datetime

router = APIRouter(prefix="/acciones", tags=["acciones"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def es_admin(current_user: dict) -> bool:
    """Verifica si el usuario es administrador"""
    return current_user.get("rol") == 1  # Rol 1 = administrador

@router.get("/", response_model=List[AccionResponseCompleta])
def list_acciones(current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.list_acciones()

@router.post("/", response_model=AccionResponse)
def create_accion(request: AccionRequest, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.create_accion(request)

@router.get("/{accion_id}", response_model=AccionResponse)
def get_accion(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_accion(accion_id)

@router.put("/{accion_id}", response_model=AccionResponse)
def update_accion(accion_id: int, request: AccionUpdateRequest, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.update_accion(accion_id, request)

@router.delete("/{accion_id}")
def delete_accion(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.delete_accion(accion_id)

@router.post("/{accion_id}/generar-certificado")
def generar_certificado(accion_id: int):
    """Genera certificado cifrado sin requerir autenticación"""
    use_case = AccionUseCase(AccionRepository())
    result = use_case.generar_certificado(accion_id)
    
    # El PDF ahora viene cifrado con contraseña
    if isinstance(result, dict) and 'pdf_cifrado' in result:
        # PDF cifrado - retornar PDF directo con contraseña en headers
        pdf_content = result["pdf_cifrado"]
        password = result["password"]
        filename = f"certificado_accion_{accion_id}_cifrado.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content)),
                "X-PDF-Password": password,
                "X-PDF-Encrypted": "true",
                "X-PDF-Filename": filename
            }
        )
    else:
        # PDF sin cifrar (fallback)
        pdf_content = result
        filename = f"certificado_accion_{accion_id}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content))
            }
        )

@router.post("/descifrar-pdf")
def descifrar_pdf_directo(request: dict, current_user=Depends(get_current_user)):
    """Descifra un PDF directamente enviado en la request"""
    try:
        from infrastructure.pdf_service import PDFService
        import base64
        
        # Obtener PDF cifrado y contraseña de la request
        pdf_cifrado_base64 = request.get('pdf_cifrado_base64')
        password = request.get('password')
        
        if not pdf_cifrado_base64 or not password:
            raise HTTPException(status_code=400, detail="Se requiere pdf_cifrado_base64 y password")
        
        # Decodificar PDF de base64
        pdf_cifrado = base64.b64decode(pdf_cifrado_base64)
        
        # Descifrar usando el servicio
        pdf_service = PDFService()
        pdf_descifrado = pdf_service.descifrar_pdf(pdf_cifrado, password)
        
        if pdf_descifrado:
            filename = "certificado_descifrado.pdf"
            return Response(
                content=pdf_descifrado,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(pdf_descifrado)),
                    "X-PDF-Encrypted": "false"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="No se pudo descifrar el PDF")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error descifrando PDF: {str(e)}")

@router.post("/{accion_id}/descifrar-certificado")
def descifrar_certificado(accion_id: int, request: DescifrarCertificadoRequest, current_user=Depends(get_current_user)):
    """Descifra un certificado PDF con la contraseña proporcionada"""
    use_case = AccionUseCase(AccionRepository())
    result = use_case.descifrar_certificado(accion_id, request.password)
    
    if result:
        filename = f"certificado_accion_{accion_id}_descifrado.pdf"
        return Response(
            content=result,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(result)),
                "X-PDF-Encrypted": "false"
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta o PDF no encontrado")

@router.get("/{accion_id}/ver-certificado")
def ver_certificado(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.ver_certificado(accion_id)

@router.patch("/{accion_id}/cifrar-certificado")
def cifrar_certificado(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.cifrar_certificado(accion_id)

@router.get("/{accion_id}/pagos")
def get_pagos(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_pagos(accion_id)

@router.get("/estado-pagos-resumen")
def list_acciones_con_estado_pagos(current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.list_acciones_con_estado_pagos()

@router.get("/{accion_id}/estado-pagos")
def get_estado_pagos(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_estado_pagos(accion_id)

# ==================== NUEVOS ENDPOINTS PARA VENTA DE ACCIONES ====================

@router.post("/{accion_id}/generar-qr")
def generar_qr_pago(accion_id: int, current_user=Depends(get_current_user)):
    """
    Genera QR para pago de acción según el método seleccionado
    """
    try:
        # Obtener la acción
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(accion_id)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        if accion.estado_accion != 1:  # Solo si está pendiente de pago
            raise HTTPException(status_code=400, detail="La acción no está pendiente de pago")
        
        # Generar QR según el método de pago
        qr_service = QRService()
        
        if accion.metodo_pago == "qr_transferencia":
            resultado = qr_service.generar_qr_transferencia(
                accion_id, 
                accion.total_pago, 
                accion.tipo_accion or "compra"
            )
        elif accion.metodo_pago == "qr_pago_movil":
            resultado = qr_service.generar_qr_pago_movil(accion_id, accion.total_pago)
        elif accion.metodo_pago == "efectivo":
            resultado = qr_service.generar_qr_efectivo(accion_id, accion.total_pago)
        else:
            raise HTTPException(status_code=400, detail=f"Método de pago no soportado: {accion.metodo_pago}")
        
        # Actualizar acción con datos del QR
        accion_repository.update_accion(accion_id, {
            "qr_data": json.dumps(resultado)
        })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando QR: {str(e)}")

@router.post("/{accion_id}/subir-comprobante")
def subir_comprobante(accion_id: int, comprobante: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Usuario sube comprobante de transferencia
    """
    try:
        # Verificar que la acción existe
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(accion_id)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        if accion.estado_accion not in [1, 2]:  # Solo si está pendiente o ya tiene comprobante
            raise HTTPException(status_code=400, detail="No se puede subir comprobante para esta acción")
        
        # Crear directorio de comprobantes si no existe
        comprobantes_dir = "comprobantes"
        os.makedirs(comprobantes_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprobante_accion_{accion_id}_{timestamp}.pdf"
        filepath = os.path.join(comprobantes_dir, filename)
        
        # Guardar el archivo
        with open(filepath, "wb") as f:
            content = comprobante.file.read()
            f.write(content)
        
        # Actualizar acción con comprobante
        from datetime import datetime
        accion_repository.update_accion(accion_id, {
            "estado_accion": 2,  # Pendiente confirmación
            "comprobante_path": filepath,
            "fecha_comprobante": datetime.now().isoformat()
        })
        
        return {
            "mensaje": "Comprobante recibido exitosamente",
            "estado": "Pendiente confirmación",
            "tiempo_estimado": "24-48 horas",
            "archivo": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo comprobante: {str(e)}")

@router.post("/{accion_id}/aprobar-pago")
def aprobar_pago_admin(accion_id: int, current_user=Depends(get_current_user)):
    """
    Admin aprueba el pago después de verificar comprobante
    """
    try:
        # Verificar que es admin
        if not es_admin(current_user):
            raise HTTPException(status_code=403, detail="Solo administradores pueden aprobar pagos")
        
        # Obtener la acción
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(accion_id)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        if accion.estado_accion != 2:  # Solo si está pendiente confirmación
            raise HTTPException(status_code=400, detail="La acción no está pendiente de confirmación")
        
        # Cambiar estado a pagado
        accion_repository.update_accion(accion_id, {
            "estado_accion": 3  # Pagado
        })
        
        # Generar certificado
        certificate_service = CertificateService()
        
        # Preparar datos para el certificado
        accion_data = {
            'id_accion': accion.id_accion,
            'id_socio': accion.id_socio,
            'tipo_accion': accion.tipo_accion,
            'cantidad_acciones': accion.cantidad_acciones,
            'precio_unitario': accion.precio_unitario,
            'total_pago': accion.total_pago,
            'metodo_pago': accion.metodo_pago,
            'socio_titular': accion.socio_titular,
            'modalidad_pago_info': f"Modalidad {accion.modalidad_pago}"
        }
        
        # Generar certificado completo (original + cifrado)
        certificado_info = certificate_service.generar_certificado_completo(accion_data, accion.id_socio)
        
        # Actualizar acción con certificado
        from datetime import datetime
        accion_repository.update_accion(accion_id, {
            "estado_accion": 4,  # Completado
            "certificado_pdf": certificado_info["certificado_original"],
            "certificado_cifrado": True,
            "fecha_emision_certificado": datetime.now().isoformat()
        })
        
        return {
            "mensaje": "Pago aprobado y certificado generado",
            "certificado_disponible": True,
            "estado": "Completado",
            "certificado_info": certificado_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aprobando pago: {str(e)}")

@router.get("/{accion_id}/descargar-certificado")
def descargar_certificado(accion_id: int, current_user=Depends(get_current_user)):
    """
    Descarga certificado - original si es el usuario correcto, cifrado si no
    """
    try:
        # Obtener la acción
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(accion_id)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        if accion.estado_accion != 4:  # Solo si está completado
            raise HTTPException(status_code=400, detail="La acción no está completada")
        
        if not accion.certificado_pdf:
            raise HTTPException(status_code=404, detail="Certificado no disponible")
        
        # Verificar si el usuario es el propietario o admin
        usuario_id = current_user.get("id_usuario")
        es_admin_user = es_admin(current_user)
        
        if accion.id_socio == usuario_id or es_admin_user:
            # Usuario correcto o admin - descargar original
            if os.path.exists(accion.certificado_pdf):
                return FileResponse(
                    path=accion.certificado_pdf,
                    filename=f"certificado_accion_{accion_id}_original.pdf",
                    media_type="application/pdf"
                )
            else:
                raise HTTPException(status_code=404, detail="Archivo de certificado no encontrado")
        else:
            # Usuario incorrecto - descargar cifrado
            certificate_service = CertificateService()
            certificado_cifrado_path = os.path.join(
                certificate_service.cifrados_dir,
                f"certificado_accion_{accion_id}_{accion.id_socio}_*_cifrado_{accion.id_socio}.bin"
            )
            
            # Buscar archivo cifrado
            import glob
            archivos_cifrados = glob.glob(certificado_cifrado_path)
            
            if not archivos_cifrados:
                raise HTTPException(status_code=404, detail="Certificado cifrado no encontrado")
            
            archivo_cifrado = archivos_cifrados[0]
            
            return FileResponse(
                path=archivo_cifrado,
                filename=f"certificado_accion_{accion_id}_cifrado.bin",
                media_type="application/octet-stream"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descargando certificado: {str(e)}")

@router.get("/{accion_id}/estado")
def get_estado_accion(accion_id: int, current_user=Depends(get_current_user)):
    """
    Obtiene el estado actual de una acción
    """
    try:
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(accion_id)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        # Mapear estados
        estados = {
            1: "Pendiente Pago",
            2: "Pendiente Confirmación",
            3: "Pagado",
            4: "Completado",
            5: "Fallido"
        }
        
        return {
            "id_accion": accion.id_accion,
            "estado_accion": accion.estado_accion,
            "estado_nombre": estados.get(accion.estado_accion, "Desconocido"),
            "metodo_pago": accion.metodo_pago,
            "total_pago": accion.total_pago,
            "certificado_disponible": accion.certificado_pdf is not None,
            "fecha_venta": accion.fecha_venta,
            "fecha_comprobante": accion.fecha_comprobante
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

# ==================== NUEVOS ENDPOINTS PARA FLUJO MEJORADO ====================

@router.post("/generar-qr-pago")
def generar_qr_pago_sin_crear_accion(current_user=Depends(get_current_user)):
    """
    Genera QR de pago sin crear acción en la BD.
    Solo crea la acción cuando se confirme el pago.
    """
    try:
        from pydantic import BaseModel
        
        class QRPaymentRequest(BaseModel):
            id_socio: int
            cantidad_acciones: int
            precio_unitario: float
            total_pago: float
            metodo_pago: str = "qr_transferencia"
            modalidad_pago: int = 1
            tipo_accion: str = "compra"
        
        # Obtener datos del request (se enviarán en el body)
        # Por ahora simularemos con datos fijos para la prueba
        
        # Crear servicio de pagos temporales
        temp_payment_service = TempPaymentService()
        
        # Datos del pago
        payment_data = {
            "id_socio": 1,  # Temporal para prueba
            "cantidad_acciones": 100,
            "precio_unitario": 50.00,
            "total_pago": 5000.00,
            "metodo_pago": "qr_transferencia",
            "modalidad_pago": 1,
            "tipo_accion": "compra",
            "id_club": 1,
            "estado_accion": 1
        }
        
        # Crear pago temporal
        temp_ref = temp_payment_service.create_temp_payment(payment_data)
        
        # Generar QR con referencia temporal
        qr_service = QRService()
        # Crear un ID numérico temporal basado en el hash de la referencia
        import hashlib
        temp_id = int(hashlib.md5(temp_ref.encode()).hexdigest()[:8], 16) % 1000000
        
        qr_result = qr_service.generar_qr_transferencia(
            temp_id,  # Usar ID numérico temporal
            payment_data["total_pago"],
            f"{payment_data['cantidad_acciones']} acciones"
        )
        
        # Actualizar QR con referencia temporal
        qr_result["datos_transferencia"]["referencia"] = temp_ref
        qr_result["datos_transferencia"]["concepto"] = f"Compra de {payment_data['cantidad_acciones']} acciones - {temp_ref}"
        
        # Guardar QR temporal
        qr_filename = f"temp_{temp_ref}.png"
        qr_temp_path = f"qr_codes/{qr_filename}"
        import shutil
        shutil.copy2(qr_result["qr_image"], qr_temp_path)
        
        return {
            "qr": {
                "tipo": qr_result["tipo"],
                "qr_image": qr_temp_path,
                "qr_url": f"/acciones/qr/{qr_filename}",
                "datos_transferencia": qr_result["datos_transferencia"],
                "instrucciones": qr_result["instrucciones"]
            },
            "datos_pago": {
                "id_socio": payment_data["id_socio"],
                "cantidad_acciones": payment_data["cantidad_acciones"],
                "precio_unitario": payment_data["precio_unitario"],
                "total_pago": payment_data["total_pago"],
                "metodo_pago": payment_data["metodo_pago"],
                "referencia_temporal": temp_ref,
                "fecha_limite": temp_payment_service.get_temp_payment(temp_ref)["fecha_limite"]
            },
            "mensaje": "QR generado exitosamente. Realiza el pago y sube el comprobante para confirmar."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando QR de pago: {str(e)}")

@router.post("/confirmar-pago")
def confirmar_pago_y_crear_accion(current_user=Depends(get_current_user)):
    """
    Confirma el pago y crea la acción en la BD.
    Solo se ejecuta después de que el usuario haya pagado.
    """
    try:
        from pydantic import BaseModel
        
        class ConfirmPaymentRequest(BaseModel):
            referencia_temporal: str
            datos_pago: dict
            comprobante: UploadFile
        
        # Por ahora simularemos la confirmación
        # En una implementación real, recibiríamos los datos del request
        
        # Crear servicios necesarios
        temp_payment_service = TempPaymentService()
        accion_repository = AccionRepository()
        certificate_service = CertificateService()
        
        # Por ahora usaremos la primera referencia temporal encontrada
        # En la implementación real vendría del request
        import glob
        temp_files = glob.glob("temp_payments/TEMP_*.json")
        if not temp_files:
            raise HTTPException(status_code=404, detail="No hay pagos temporales pendientes")
        
        # Tomar el más reciente
        temp_ref = os.path.basename(temp_files[-1]).replace('.json', '')
        
        # Verificar que el pago temporal existe
        temp_payment = temp_payment_service.get_temp_payment(temp_ref)
        if not temp_payment:
            raise HTTPException(status_code=404, detail="Pago temporal no encontrado o expirado")
        
        payment_data = temp_payment["datos_pago"]
        
        # Simular comprobante
        comprobante_path = f"comprobantes/temp_comprobante_{temp_ref}.pdf"
        os.makedirs("comprobantes", exist_ok=True)
        with open(comprobante_path, "w") as f:
            f.write(f"Comprobante simulado para {temp_ref}")
        
        # Confirmar pago temporal
        temp_payment_service.confirm_temp_payment(temp_ref, comprobante_path)
        
        # Crear acción en la BD
        from datetime import datetime
        from schemas.accion import AccionRequest
        
        accion_data = AccionRequest(
            id_club=payment_data["id_club"],
            id_socio=payment_data["id_socio"],
            modalidad_pago=payment_data["modalidad_pago"],
            estado_accion=4,  # Completado directamente
            certificado_pdf=None,
            certificado_cifrado=False,
            tipo_accion=payment_data["tipo_accion"],
            cantidad_acciones=payment_data["cantidad_acciones"],
            precio_unitario=payment_data["precio_unitario"],
            total_pago=payment_data["total_pago"],
            metodo_pago=payment_data["metodo_pago"]
        )
        
        accion_creada = accion_repository.create_accion(accion_data)
        
        # Generar certificado
        certificado_data = {
            'id_accion': accion_creada.id_accion,
            'id_socio': accion_creada.id_socio,
            'tipo_accion': accion_creada.tipo_accion,
            'cantidad_acciones': accion_creada.cantidad_acciones,
            'precio_unitario': accion_creada.precio_unitario,
            'total_pago': accion_creada.total_pago,
            'metodo_pago': accion_creada.metodo_pago,
            'socio_titular': f"Socio {accion_creada.id_socio}",  # Temporal
            'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
        }
        
        # Generar certificado completo
        certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
        
        # Actualizar acción con certificado
        accion_repository.update_accion(accion_creada.id_accion, {
            "certificado_pdf": certificado_info["certificado_original"],
            "certificado_cifrado": True,
            "fecha_emision_certificado": datetime.now().isoformat()
        })
        
        # Limpiar pago temporal
        temp_payment_service.delete_temp_payment(temp_ref)
        
        return {
            "mensaje": "Pago confirmado y acción creada exitosamente",
            "accion": {
                "id_accion": accion_creada.id_accion,
                "id_socio": accion_creada.id_socio,
                "cantidad_acciones": accion_creada.cantidad_acciones,
                "precio_unitario": accion_creada.precio_unitario,
                "total_pago": accion_creada.total_pago,
                "metodo_pago": accion_creada.metodo_pago,
                "estado_accion": 4,
                "estado_nombre": "Completado",
                "fecha_creacion": datetime.now().isoformat()
            },
            "certificado": {
                "disponible": True,
                "ruta": certificado_info["certificado_original"],
                "fecha_generacion": certificado_info["fecha_generacion"]
            },
            "referencia_temporal": temp_ref
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirmando pago: {str(e)}")

@router.get("/pagos-temporales/stats")
def get_temp_payments_stats(current_user=Depends(get_current_user)):
    """
    Obtiene estadísticas de pagos temporales (solo para administradores)
    """
    try:
        if not es_admin(current_user):
            raise HTTPException(status_code=403, detail="Solo administradores pueden ver estadísticas")
        
        temp_payment_service = TempPaymentService()
        stats = temp_payment_service.get_payment_stats()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@router.post("/pagos-temporales/limpiar")
def limpiar_pagos_temporales_expirados(current_user=Depends(get_current_user)):
    """
    Limpia pagos temporales expirados (solo para administradores)
    """
    try:
        if not es_admin(current_user):
            raise HTTPException(status_code=403, detail="Solo administradores pueden limpiar pagos temporales")
        
        temp_payment_service = TempPaymentService()
        eliminados = temp_payment_service.cleanup_expired_payments()
        
        return {
            "mensaje": f"Se eliminaron {eliminados} pagos temporales expirados",
            "archivos_eliminados": eliminados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando pagos temporales: {str(e)}")

# ==================== ENDPOINTS PARA SERVIR ARCHIVOS ====================

@router.get("/qr/{filename}")
def servir_qr(filename: str):
    """
    Sirve archivos QR para que puedan ser accedidos desde el frontend
    """
    try:
        import os
        
        # Validar que el archivo es un QR
        if not filename.startswith(('transferencia_', 'temp_TEMP_', 'pago_movil_')):
            raise HTTPException(status_code=403, detail="Archivo no autorizado")
        
        # Construir ruta del archivo
        qr_path = os.path.join("qr_codes", filename)
        
        # Verificar que el archivo existe
        if not os.path.exists(qr_path):
            raise HTTPException(status_code=404, detail="Archivo QR no encontrado")
        
        # Retornar el archivo
        return FileResponse(
            path=qr_path,
            filename=filename,
            media_type="image/png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sirviendo QR: {str(e)}")

@router.get("/certificados/{filename}")
def servir_certificado(filename: str, current_user=Depends(get_current_user)):
    """
    Sirve certificados para descarga con validación de autorización.
    Si el usuario es el socio propietario, retorna PDF original.
    Si no es el propietario, retorna PDF cifrado.
    """
    try:
        import os
        from infrastructure.accion_repository import AccionRepository
        from infrastructure.certificate_service import CertificateService
        
        # Validar que el archivo es un certificado
        if not filename.startswith('certificado_accion_'):
            raise HTTPException(status_code=403, detail="Archivo no autorizado")
        
        # Extraer ID de acción del nombre del archivo
        # Formato: certificado_accion_{id_accion}_{id_socio}_{fecha}.pdf
        parts = filename.replace('.pdf', '').split('_')
        if len(parts) < 4:
            raise HTTPException(status_code=400, detail="Formato de archivo inválido")
        
        try:
            id_accion = int(parts[2])
            id_socio_propietario = int(parts[3])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="No se pudo extraer ID de acción del archivo")
        
        # Verificar que la acción existe
        accion_repository = AccionRepository()
        accion = accion_repository.get_accion(id_accion)
        
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        # Verificar autorización
        es_propietario = False
        
        # Si el usuario es admin, puede ver cualquier certificado
        if current_user["rol"] == 1:  # Admin
            es_propietario = True
        else:
            # Si el usuario es socio, verificar si es el propietario
            if current_user["rol"] == 4:  # Socio
                # Obtener el socio del usuario actual
                from infrastructure.socio_repository import SocioRepository
                socio_repository = SocioRepository()
                socio = socio_repository.get_socio_by_usuario_id(current_user["id_usuario"])
                
                if socio and socio.id_socio == id_socio_propietario:
                    es_propietario = True
        
        # Determinar qué archivo servir
        if es_propietario:
            # Usuario autorizado: servir PDF original
            archivo_path = os.path.join("certificados", "originales", filename)
            media_type = "application/pdf"
            
            if not os.path.exists(archivo_path):
                raise HTTPException(status_code=404, detail="Certificado original no encontrado")
                
        else:
            # Usuario no autorizado: servir PDF falso con contenido cifrado
            # Buscar archivo cifrado falso
            base_name = filename.replace('.pdf', '')
            archivo_falso = f"{base_name}_cifrado_{current_user['id_usuario']}.pdf"
            archivo_path = os.path.join("certificados", "cifrados", archivo_falso)
            
            if not os.path.exists(archivo_path):
                # Si no existe el archivo falso específico, generar uno
                certificate_service = CertificateService()
                
                # Generar archivo falso para este usuario
                archivo_original = os.path.join("certificados", "originales", filename)
                if os.path.exists(archivo_original):
                    archivo_path = certificate_service.generar_certificado_falso(
                        archivo_original, current_user["id_usuario"]
                    )
                else:
                    raise HTTPException(status_code=404, detail="Certificado original no encontrado")
            
            media_type = "application/pdf"
            filename = archivo_falso
        
        return FileResponse(
            path=archivo_path,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sirviendo certificado: {str(e)}")

# ==================== ENDPOINTS PARA STRIPE ====================

@router.post("/stripe/crear-pago", response_model=StripePaymentResponse)
def crear_pago_stripe(request: StripePaymentRequest, current_user=Depends(get_current_user)):
    """
    Crea un pago con Stripe y retorna datos para el frontend.
    Para Bolivia, genera un QR con datos de transferencia bancaria.
    """
    try:
        # Crear servicio de pagos temporales
        temp_payment_service = TempPaymentService()
        
        # Datos del pago
        payment_data = {
            "id_socio": request.id_socio,
            "cantidad_acciones": request.cantidad_acciones,
            "precio_unitario": request.precio_unitario,
            "total_pago": request.total_pago,
            "metodo_pago": request.metodo_pago,
            "modalidad_pago": request.modalidad_pago,
            "tipo_accion": request.tipo_accion,
            "id_club": 1, # Asumimos club 1 por defecto
            "estado_accion": 1 # Pendiente Pago
        }
        
        # Crear pago temporal
        temp_ref = temp_payment_service.create_temp_payment(payment_data)
        payment_data["referencia_temporal"] = temp_ref
        
        # Crear pago en Stripe
        stripe_service = StripeService()
        stripe_result = stripe_service.crear_pago_qr_boliviano(payment_data)
        
        return StripePaymentResponse(
            payment_intent_id=stripe_result["payment_intent_id"],
            client_secret=stripe_result["client_secret"],
            amount=stripe_result["amount"],
            currency=stripe_result["currency"],
            status=stripe_result["status"],
            metadata=stripe_result["metadata"],
            description=stripe_result["description"],
            qr_data=stripe_result["qr_data"],
            metodo_pago=stripe_result["metodo_pago"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pago con Stripe: {str(e)}")

@router.get("/stripe/verificar-pago/{payment_intent_id}")
def verificar_pago_stripe(payment_intent_id: str, current_user=Depends(get_current_user)):
    """
    Verifica el estado de un pago en Stripe
    """
    try:
        stripe_service = StripeService()
        pago_info = stripe_service.verificar_pago(payment_intent_id)
        
        return {
            "payment_intent_id": pago_info["payment_intent_id"],
            "status": pago_info["status"],
            "amount": pago_info["amount"],
            "currency": pago_info["currency"],
            "metadata": pago_info["metadata"],
            "created": pago_info["created"],
            "charges": pago_info["charges"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando pago: {str(e)}")

@router.post("/stripe/confirmar-pago/{payment_intent_id}")
def confirmar_pago_stripe(payment_intent_id: str, current_user=Depends(get_current_user)):
    """
    Confirma un pago en Stripe (para pagos manuales)
    """
    try:
        stripe_service = StripeService()
        pago_confirmado = stripe_service.confirmar_pago(payment_intent_id)
        
        # Si el pago se confirmó exitosamente, crear la acción
        if pago_confirmado["status"] == "succeeded":
            metadata = pago_confirmado["metadata"]
            
            # Crear acción en la BD
            accion_repository = AccionRepository()
            certificate_service = CertificateService()
            
            from schemas.accion import AccionRequest
            
            accion_request_data = AccionRequest(
                id_club=int(metadata["id_club"]) if "id_club" in metadata else 1,
                id_socio=int(metadata["socio_id"]),
                modalidad_pago=int(metadata["modalidad_pago"]) if "modalidad_pago" in metadata else 1,
                estado_accion=4,  # Completado directamente
                certificado_pdf=None,
                certificado_cifrado=False,
                tipo_accion=metadata["tipo_accion"],
                cantidad_acciones=int(metadata["cantidad_acciones"]),
                precio_unitario=float(metadata["precio_unitario"]),
                total_pago=float(pago_confirmado["amount"]) / 100,  # Convertir de centavos
                metodo_pago="stripe"
            )
            
            accion_creada = accion_repository.create_accion(accion_request_data)
            
            # Generar certificado
            socio_repository = SocioRepository()
            socio = socio_repository.get_socio(accion_creada.id_socio)
            socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

            certificado_data = {
                'id_accion': accion_creada.id_accion,
                'id_socio': accion_creada.id_socio,
                'tipo_accion': accion_creada.tipo_accion,
                'cantidad_acciones': accion_creada.cantidad_acciones,
                'precio_unitario': accion_creada.precio_unitario,
                'total_pago': accion_creada.total_pago,
                'metodo_pago': accion_creada.metodo_pago,
                'socio_titular': socio_titular_nombre,
                'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
            }
            
            # Generar certificado completo (original + cifrado)
            certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
            
            # Actualizar acción con certificado
            accion_repository.update_accion(accion_creada.id_accion, {
                "certificado_pdf": certificado_info["certificado_original"],
                "certificado_cifrado": True,
                "fecha_emision_certificado": datetime.now().isoformat()
            })
            
            # Limpiar pago temporal si existe
            temp_ref = metadata.get("referencia_temporal")
            if temp_ref:
                temp_payment_service = TempPaymentService()
                temp_payment_service.delete_temp_payment(temp_ref)
            
            return {
                "mensaje": "Pago confirmado y acción creada exitosamente",
                "pago": pago_confirmado,
                "accion": {
                    "id_accion": accion_creada.id_accion,
                    "id_socio": accion_creada.id_socio,
                    "cantidad_acciones": accion_creada.cantidad_acciones,
                    "precio_unitario": accion_creada.precio_unitario,
                    "total_pago": accion_creada.total_pago,
                    "metodo_pago": accion_creada.metodo_pago,
                    "estado_accion": 4,
                    "estado_nombre": "Completado",
                    "fecha_creacion": datetime.now().isoformat()
                },
                "certificado": {
                    "disponible": True,
                    "ruta": certificado_info["certificado_original"],
                    "fecha_generacion": certificado_info["fecha_generacion"]
                }
            }
        else:
            return {
                "mensaje": "Pago no completado",
                "pago": pago_confirmado
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirmando pago: {str(e)}")

@router.post("/stripe/cancelar-pago/{payment_intent_id}")
def cancelar_pago_stripe(payment_intent_id: str, current_user=Depends(get_current_user)):
    """
    Cancela un pago en Stripe
    """
    try:
        stripe_service = StripeService()
        pago_cancelado = stripe_service.cancelar_pago(payment_intent_id)
        
        # Limpiar pago temporal si existe
        metadata = pago_cancelado.get("metadata", {})
        temp_ref = metadata.get("referencia_temporal")
        if temp_ref:
            temp_payment_service = TempPaymentService()
            temp_payment_service.delete_temp_payment(temp_ref)
        
        return {
            "mensaje": "Pago cancelado exitosamente",
            "pago": pago_cancelado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelando pago: {str(e)}")

@router.get("/stripe/configuracion")
def obtener_configuracion_stripe():
    """
    Obtiene configuración pública de Stripe para el frontend
    """
    try:
        stripe_service = StripeService()
        config = stripe_service.obtener_configuracion_publica()
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

# ==================== WEBHOOKS DE STRIPE ====================

@router.post("/stripe/webhook", response_model=StripeWebhookResponse)
def webhook_stripe(request: Request):
    """
    Webhook para recibir eventos de Stripe
    """
    try:
        payload = request.body
        signature = request.headers.get('stripe-signature')
        
        stripe_service = StripeService()
        webhook_result = stripe_service.procesar_webhook(payload.decode('utf-8'), signature)
        
        # Procesar el resultado del webhook
        if webhook_result.get("action") == "crear_accion":
            # Crear acción automáticamente cuando el pago es exitoso
            metadata = webhook_result.get("metadata", {})
            
            try:
                # Crear acción en la BD
                accion_repository = AccionRepository()
                certificate_service = CertificateService()
                
                from schemas.accion import AccionRequest
                
                accion_request_data = AccionRequest(
                    id_club=1,  # Por defecto
                    id_socio=int(metadata["socio_id"]),
                    modalidad_pago=1,  # Por defecto
                    estado_accion=4,  # Completado
                    certificado_pdf=None,
                    certificado_cifrado=False,
                    tipo_accion=metadata["tipo_accion"],
                    cantidad_acciones=int(metadata["cantidad_acciones"]),
                    precio_unitario=float(metadata["precio_unitario"]),
                    total_pago=float(webhook_result["amount"]) / 100,  # Convertir de centavos
                    metodo_pago="stripe"
                )
                
                accion_creada = accion_repository.create_accion(accion_request_data)
                
                # Generar certificado
                socio_repository = SocioRepository()
                socio = socio_repository.get_socio(accion_creada.id_socio)
                socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

                certificado_data = {
                    'id_accion': accion_creada.id_accion,
                    'id_socio': accion_creada.id_socio,
                    'tipo_accion': accion_creada.tipo_accion,
                    'cantidad_acciones': accion_creada.cantidad_acciones,
                    'precio_unitario': accion_creada.precio_unitario,
                    'total_pago': accion_creada.total_pago,
                    'metodo_pago': accion_creada.metodo_pago,
                    'socio_titular': socio_titular_nombre,
                    'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
                }
                
                # Generar certificado completo (original + cifrado)
                certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
                
                # Actualizar acción con certificado
                accion_repository.update_accion(accion_creada.id_accion, {
                    "certificado_pdf": certificado_info["certificado_original"],
                    "certificado_cifrado": True,
                    "fecha_emision_certificado": datetime.now().isoformat()
                })
                
                # Limpiar pago temporal si existe
                temp_ref = metadata.get("referencia_temporal")
                if temp_ref:
                    temp_payment_service = TempPaymentService()
                    temp_payment_service.delete_temp_payment(temp_ref)
                
                logging.info(f"Acción creada automáticamente vía webhook: {accion_creada.id_accion}")
                
            except Exception as e:
                logging.error(f"Error creando acción vía webhook: {str(e)}")
        
        elif webhook_result.get("action") == "limpiar_pago_temporal":
            # Limpiar pago temporal cuando se cancela
            metadata = webhook_result.get("metadata", {})
            temp_ref = metadata.get("referencia_temporal")
            if temp_ref:
                temp_payment_service = TempPaymentService()
                temp_payment_service.delete_temp_payment(temp_ref)
                logging.info(f"Pago temporal limpiado vía webhook: {temp_ref}")
        
        return StripeWebhookResponse(**webhook_result)
        
    except Exception as e:
        logging.error(f"Error procesando webhook de Stripe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")

# ==================== ENDPOINTS PARA MERCADOPAGO (MÁS FÁCIL) ====================

@router.post("/mercadopago/crear-pago", response_model=MercadoPagoPaymentResponse)
def crear_pago_mercadopago(request: MercadoPagoPaymentRequest, current_user=Depends(get_current_user)):
    """
    Crea un pago con MercadoPago y retorna datos para el frontend.
    MÁS FÁCIL que Stripe - API de prueba inmediata.
    """
    try:
        # Crear servicio de pagos temporales
        temp_payment_service = TempPaymentService()
        
        # Datos del pago
        payment_data = {
            "id_socio": request.id_socio,
            "cantidad_acciones": request.cantidad_acciones,
            "precio_unitario": request.precio_unitario,
            "total_pago": request.total_pago,
            "metodo_pago": request.metodo_pago,
            "modalidad_pago": request.modalidad_pago,
            "tipo_accion": request.tipo_accion,
            "id_club": 1, # Asumimos club 1 por defecto
            "estado_accion": 1 # Pendiente Pago
        }
        
        # Crear pago temporal
        temp_ref = temp_payment_service.create_temp_payment(payment_data)
        payment_data["referencia_temporal"] = temp_ref
        
        # Crear pago en MercadoPago
        mercadopago_service = MercadoPagoService()
        mp_result = mercadopago_service.crear_pago_qr(payment_data)
        
        # Generar QR para transferencia bancaria
        qr_info = mercadopago_service.generar_qr_transferencia_bolivia(payment_data)
        
        return MercadoPagoPaymentResponse(
            preference_id=mp_result["preference_id"],
            init_point=mp_result["init_point"],
            sandbox_init_point=mp_result["sandbox_init_point"],
            status=mp_result["status"],
            amount=mp_result["amount"],
            currency=mp_result["currency"],
            external_reference=mp_result["external_reference"],
            metadata=mp_result["metadata"],
            qr_code=mp_result["qr_code"],
            checkout_url=mp_result["checkout_url"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pago con MercadoPago: {str(e)}")

@router.get("/mercadopago/verificar-pago/{preference_id}")
def verificar_pago_mercadopago(preference_id: str, current_user=Depends(get_current_user)):
    """
    Verifica el estado de un pago en MercadoPago
    """
    try:
        mercadopago_service = MercadoPagoService()
        pago_info = mercadopago_service.verificar_pago(preference_id)
        
        return {
            "preference_id": pago_info["preference_id"],
            "status": pago_info["status"],
            "external_reference": pago_info["external_reference"],
            "metadata": pago_info["metadata"],
            "init_point": pago_info["init_point"],
            "sandbox_init_point": pago_info["sandbox_init_point"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando pago: {str(e)}")

@router.get("/mercadopago/buscar-pagos/{external_reference}")
def buscar_pagos_por_referencia(external_reference: str, current_user=Depends(get_current_user)):
    """
    Busca pagos por referencia externa en MercadoPago
    """
    try:
        mercadopago_service = MercadoPagoService()
        pagos_info = mercadopago_service.buscar_pagos_por_referencia(external_reference)
        
        return {
            "total": pagos_info["total"],
            "payments": pagos_info["payments"],
            "external_reference": pagos_info["external_reference"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando pagos: {str(e)}")

@router.post("/mercadopago/confirmar-pago/{external_reference}")
def confirmar_pago_mercadopago(external_reference: str, current_user=Depends(get_current_user)):
    """
    Confirma un pago en MercadoPago y crea la acción
    """
    try:
        mercadopago_service = MercadoPagoService()
        
        # Buscar pagos por referencia
        pagos_info = mercadopago_service.buscar_pagos_por_referencia(external_reference)
        
        if pagos_info["total"] == 0:
            raise HTTPException(status_code=404, detail="No se encontraron pagos para esta referencia")
        
        # Verificar si hay algún pago aprobado
        pago_aprobado = None
        for payment in pagos_info["payments"]:
            if payment["status"] == "approved":
                pago_aprobado = payment
                break
        
        if not pago_aprobado:
            return {
                "mensaje": "No hay pagos aprobados para esta referencia",
                "total_pagos": pagos_info["total"],
                "pagos": pagos_info["payments"]
            }
        
        # Obtener detalles del pago
        pago_detalles = mercadopago_service.obtener_pago(pago_aprobado["id"])
        
        # Crear acción en la BD
        accion_repository = AccionRepository()
        certificate_service = CertificateService()
        
        from schemas.accion import AccionRequest
        
        metadata = pago_detalles["metadata"]
        accion_request_data = AccionRequest(
            id_club=1,  # Por defecto
            id_socio=int(metadata["socio_id"]),
            modalidad_pago=1,  # Por defecto
            estado_accion=4,  # Completado
            certificado_pdf=None,
            certificado_cifrado=False,
            tipo_accion=metadata["tipo_accion"],
            cantidad_acciones=int(metadata["cantidad_acciones"]),
            precio_unitario=float(metadata["precio_unitario"]),
            total_pago=float(pago_detalles["transaction_amount"]),
            metodo_pago="mercadopago"
        )
        
        accion_creada = accion_repository.create_accion(accion_request_data)
        
        # Generar certificado
        socio_repository = SocioRepository()
        socio = socio_repository.get_socio(accion_creada.id_socio)
        socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

        certificado_data = {
            'id_accion': accion_creada.id_accion,
            'id_socio': accion_creada.id_socio,
            'tipo_accion': accion_creada.tipo_accion,
            'cantidad_acciones': accion_creada.cantidad_acciones,
            'precio_unitario': accion_creada.precio_unitario,
            'total_pago': accion_creada.total_pago,
            'metodo_pago': accion_creada.metodo_pago,
            'socio_titular': socio_titular_nombre,
            'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
        }
        
        # Generar certificado completo (original + cifrado)
        certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
        
        # Actualizar acción con certificado
        accion_repository.update_accion(accion_creada.id_accion, {
            "certificado_pdf": certificado_info["certificado_original"],
            "certificado_cifrado": True,
            "fecha_emision_certificado": datetime.now().isoformat()
        })
        
        # Limpiar pago temporal
        temp_payment_service = TempPaymentService()
        temp_payment_service.delete_temp_payment(external_reference)
        
        return {
            "mensaje": "Pago confirmado y acción creada exitosamente",
            "pago": pago_detalles,
            "accion": {
                "id_accion": accion_creada.id_accion,
                "id_socio": accion_creada.id_socio,
                "cantidad_acciones": accion_creada.cantidad_acciones,
                "precio_unitario": accion_creada.precio_unitario,
                "total_pago": accion_creada.total_pago,
                "metodo_pago": accion_creada.metodo_pago,
                "estado_accion": 4,
                "estado_nombre": "Completado",
                "fecha_creacion": datetime.now().isoformat()
            },
            "certificado": {
                "disponible": True,
                "ruta": certificado_info["certificado_original"],
                "fecha_generacion": certificado_info["fecha_generacion"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirmando pago: {str(e)}")

@router.get("/mercadopago/configuracion")
def obtener_configuracion_mercadopago():
    """
    Obtiene configuración pública de MercadoPago para el frontend
    """
    try:
        mercadopago_service = MercadoPagoService()
        config = mercadopago_service.obtener_configuracion_publica()
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

@router.post("/mercadopago/webhook", response_model=MercadoPagoWebhookResponse)
def webhook_mercadopago(request: Request):
    """
    Webhook para recibir eventos de MercadoPago
    """
    try:
        webhook_data = request.json()
        
        mercadopago_service = MercadoPagoService()
        webhook_result = mercadopago_service.procesar_webhook(webhook_data)
        
        # Procesar el resultado del webhook
        if webhook_result.get("action") == "crear_accion":
            # Crear acción automáticamente cuando el pago es exitoso
            metadata = webhook_result.get("metadata", {})
            
            try:
                # Crear acción en la BD
                accion_repository = AccionRepository()
                certificate_service = CertificateService()
                
                from schemas.accion import AccionRequest
                
                accion_request_data = AccionRequest(
                    id_club=1,  # Por defecto
                    id_socio=int(metadata["socio_id"]),
                    modalidad_pago=1,  # Por defecto
                    estado_accion=4,  # Completado
                    certificado_pdf=None,
                    certificado_cifrado=False,
                    tipo_accion=metadata["tipo_accion"],
                    cantidad_acciones=int(metadata["cantidad_acciones"]),
                    precio_unitario=float(metadata["precio_unitario"]),
                    total_pago=0.00,  # Se actualizará con el monto real
                    metodo_pago="mercadopago"
                )
                
                accion_creada = accion_repository.create_accion(accion_request_data)
                
                # Generar certificado
                socio_repository = SocioRepository()
                socio = socio_repository.get_socio(accion_creada.id_socio)
                socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

                certificado_data = {
                    'id_accion': accion_creada.id_accion,
                    'id_socio': accion_creada.id_socio,
                    'tipo_accion': accion_creada.tipo_accion,
                    'cantidad_acciones': accion_creada.cantidad_acciones,
                    'precio_unitario': accion_creada.precio_unitario,
                    'total_pago': accion_creada.total_pago,
                    'metodo_pago': accion_creada.metodo_pago,
                    'socio_titular': socio_titular_nombre,
                    'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
                }
                
                # Generar certificado completo (original + cifrado)
                certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
                
                # Actualizar acción con certificado
                accion_repository.update_accion(accion_creada.id_accion, {
                    "certificado_pdf": certificado_info["certificado_original"],
                    "certificado_cifrado": True,
                    "fecha_emision_certificado": datetime.now().isoformat()
                })
                
                # Limpiar pago temporal si existe
                temp_ref = metadata.get("referencia_temporal")
                if temp_ref:
                    temp_payment_service = TempPaymentService()
                    temp_payment_service.delete_temp_payment(temp_ref)
                
                logging.info(f"Acción creada automáticamente vía webhook MercadoPago: {accion_creada.id_accion}")
                
            except Exception as e:
                logging.error(f"Error creando acción vía webhook MercadoPago: {str(e)}")
        
        return MercadoPagoWebhookResponse(**webhook_result)
        
    except Exception as e:
        logging.error(f"Error procesando webhook de MercadoPago: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")

# ==================== ENDPOINTS PARA PAYPAL (MÁS FÁCIL) ====================

@router.post("/paypal/crear-pago", response_model=PayPalPaymentResponse)
def crear_pago_paypal(request: PayPalPaymentRequest, current_user=Depends(get_current_user)):
    """
    Crea un pago con PayPal y retorna datos para el frontend.
    MÁS FÁCIL que todos - API de prueba inmediata.
    """
    try:
        # Crear servicio de pagos temporales
        temp_payment_service = TempPaymentService()
        
        # Datos del pago
        payment_data = {
            "id_socio": request.id_socio,
            "cantidad_acciones": request.cantidad_acciones,
            "precio_unitario": request.precio_unitario,
            "total_pago": request.total_pago,
            "metodo_pago": request.metodo_pago,
            "modalidad_pago": request.modalidad_pago,
            "tipo_accion": request.tipo_accion,
            "id_club": 1, # Asumimos club 1 por defecto
            "estado_accion": 1 # Pendiente Pago
        }
        
        # Crear pago temporal
        temp_ref = temp_payment_service.create_temp_payment(payment_data)
        payment_data["referencia_temporal"] = temp_ref
        
        # Crear pago en PayPal
        paypal_service = PayPalService()
        paypal_result = paypal_service.crear_pago(payment_data)
        
        return PayPalPaymentResponse(
            payment_id=paypal_result["payment_id"],
            state=paypal_result["state"],
            intent=paypal_result["intent"],
            amount=paypal_result["amount"],
            approval_url=paypal_result["approval_url"],
            external_reference=paypal_result["external_reference"],
            metadata=paypal_result["metadata"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pago con PayPal: {str(e)}")

@router.post("/paypal/ejecutar-pago", response_model=PayPalPaymentResponse)
def ejecutar_pago_paypal(request: PayPalExecuteRequest, current_user=Depends(get_current_user)):
    """
    Ejecuta un pago de PayPal después de la aprobación del usuario
    """
    try:
        paypal_service = PayPalService()
        pago_ejecutado = paypal_service.ejecutar_pago(request.payment_id, request.payer_id)
        
        # Si el pago se ejecutó exitosamente, crear la acción
        if pago_ejecutado["state"] == "approved":
            metadata = pago_ejecutado["metadata"]
            
            # Crear acción en la BD
            accion_repository = AccionRepository()
            certificate_service = CertificateService()
            
            from schemas.accion import AccionRequest
            
            accion_request_data = AccionRequest(
                id_club=1,  # Por defecto
                id_socio=int(metadata["socio_id"]),
                modalidad_pago=1,  # Por defecto
                estado_accion=4,  # Completado
                certificado_pdf=None,
                certificado_cifrado=False,
                tipo_accion=metadata["tipo_accion"],
                cantidad_acciones=int(metadata["cantidad_acciones"]),
                precio_unitario=float(metadata["precio_unitario"]),
                total_pago=float(pago_ejecutado["amount"]["total"]),
                metodo_pago="paypal"
            )
            
            accion_creada = accion_repository.create_accion(accion_request_data)
            
            # Generar certificado
            socio_repository = SocioRepository()
            socio = socio_repository.get_socio(accion_creada.id_socio)
            socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

            certificado_data = {
                'id_accion': accion_creada.id_accion,
                'id_socio': accion_creada.id_socio,
                'tipo_accion': accion_creada.tipo_accion,
                'cantidad_acciones': accion_creada.cantidad_acciones,
                'precio_unitario': accion_creada.precio_unitario,
                'total_pago': accion_creada.total_pago,
                'metodo_pago': accion_creada.metodo_pago,
                'socio_titular': socio_titular_nombre,
                'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
            }
            
            # Generar certificado completo (original + cifrado)
            certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
            
            # Actualizar acción con certificado
            accion_repository.update_accion(accion_creada.id_accion, {
                "certificado_pdf": certificado_info["certificado_original"],
                "certificado_cifrado": True,
                "fecha_emision_certificado": datetime.now().isoformat()
            })
            
            # Limpiar pago temporal
            temp_ref = pago_ejecutado["external_reference"]
            temp_payment_service = TempPaymentService()
            temp_payment_service.delete_temp_payment(temp_ref)
            
            return {
                "mensaje": "Pago ejecutado y acción creada exitosamente",
                "pago": pago_ejecutado,
                "accion": {
                    "id_accion": accion_creada.id_accion,
                    "id_socio": accion_creada.id_socio,
                    "cantidad_acciones": accion_creada.cantidad_acciones,
                    "precio_unitario": accion_creada.precio_unitario,
                    "total_pago": accion_creada.total_pago,
                    "metodo_pago": accion_creada.metodo_pago,
                    "estado_accion": 4,
                    "estado_nombre": "Completado",
                    "fecha_creacion": datetime.now().isoformat()
                },
                "certificado": {
                    "disponible": True,
                    "ruta": certificado_info["certificado_original"],
                    "fecha_generacion": certificado_info["fecha_generacion"]
                }
            }
        else:
            return {
                "mensaje": "Pago no aprobado",
                "pago": pago_ejecutado
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando pago: {str(e)}")

@router.get("/paypal/obtener-pago/{payment_id}")
def obtener_pago_paypal(payment_id: str, current_user=Depends(get_current_user)):
    """
    Obtiene detalles de un pago de PayPal
    """
    try:
        paypal_service = PayPalService()
        pago_info = paypal_service.obtener_pago(payment_id)
        
        return pago_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pago: {str(e)}")

@router.get("/paypal/configuracion")
def obtener_configuracion_paypal():
    """
    Obtiene configuración pública de PayPal para el frontend
    """
    try:
        paypal_service = PayPalService()
        config = paypal_service.obtener_configuracion_publica()
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

# ==================== ENDPOINTS PARA PAGO SIMULADO (SIN SERVICIOS EXTERNOS) ====================

@router.post("/simular-pago/crear-qr")
def crear_qr_pago_simulado(request: AccionRequest, current_user=Depends(get_current_user)):
    """
    Crea un QR de pago simulado y datos temporales.
    NO crea la acción aún - solo prepara el pago.
    """
    try:
        # Crear servicio de pagos temporales
        temp_payment_service = TempPaymentService()
        
        # Datos del pago
        payment_data = {
            "id_socio": request.id_socio,
            "cantidad_acciones": 1,  # Fijo en 1 por defecto
            "precio_unitario": request.total_pago,  # El precio unitario es igual al total
            "total_pago": request.total_pago,
            "metodo_pago": "transferencia",
            "modalidad_pago": request.modalidad_pago,
            "tipo_accion": request.tipo_accion,
            "id_club": request.id_club or 1,  # Por defecto 1 si no viene
            "estado_accion": 1  # Pendiente Pago
        }
        
        # Crear pago temporal
        temp_ref = temp_payment_service.create_temp_payment(payment_data)
        payment_data["referencia_temporal"] = temp_ref
        
        # Generar QR de transferencia bancaria
        qr_service = QRService()
        qr_data = qr_service.generar_qr_transferencia_bolivia(
            temp_ref,
            payment_data["total_pago"],
            payment_data["cantidad_acciones"],
            temp_ref
        )
        
        return {
            "mensaje": "QR de pago generado exitosamente",
            "referencia_temporal": temp_ref,
            "qr_data": qr_data,
            "pago_info": {
                "id_socio": payment_data["id_socio"],
                "cantidad_acciones": payment_data["cantidad_acciones"],
                "precio_unitario": payment_data["precio_unitario"],
                "total_pago": payment_data["total_pago"],
                "metodo_pago": payment_data["metodo_pago"],
                "modalidad_pago": payment_data["modalidad_pago"],
                "tipo_accion": payment_data["tipo_accion"]
            },
            "instrucciones": [
                "1. Realiza la transferencia bancaria con los datos del QR",
                "2. Envía el comprobante por WhatsApp al 12345678",
                "3. El pago se confirmará automáticamente",
                "4. Tu acción será activada inmediatamente"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando QR de pago: {str(e)}")

@router.post("/simular-pago/confirmar-pago")
def confirmar_pago_simulado(
    referencia_temporal: str,
    current_user=Depends(get_current_user)
):
    """
    Confirma un pago simulado sin subir comprobante.
    Crea la acción automáticamente y genera el certificado.
    """
    try:
        # Verificar que el pago temporal existe
        temp_payment_service = TempPaymentService()
        payment_data = temp_payment_service.get_temp_payment(referencia_temporal)
        
        if not payment_data:
            raise HTTPException(status_code=404, detail="Pago temporal no encontrado o expirado")
        
        # Extraer datos del pago (están en datos_pago)
        pago_data = payment_data.get("datos_pago", payment_data)
        
        
        # Marcar pago como confirmado
        temp_payment_service.confirm_temp_payment(referencia_temporal)
        
        # Crear acción en la BD
        accion_repository = AccionRepository()
        certificate_service = CertificateService()
        
        accion_request_data = AccionRequest(
            id_club=pago_data.get("id_club", 1),  # Por defecto 1
            id_socio=pago_data["id_socio"],
            modalidad_pago=pago_data["modalidad_pago"],
            estado_accion=2,  # Aprobada
            certificado_pdf=None,
            certificado_cifrado=False,
            tipo_accion=pago_data["tipo_accion"],
            cantidad_acciones=pago_data["cantidad_acciones"],
            precio_unitario=pago_data["precio_unitario"],
            total_pago=pago_data["total_pago"],
            metodo_pago=pago_data["metodo_pago"]
        )
        
        accion_creada = accion_repository.create_accion(accion_request_data)
        
        # Crear registro en pago_accion
        from infrastructure.pago_repository import PagoRepository
        from schemas.pago import PagoRequest as PagoSchemaRequest
        
        pago_repository = PagoRepository()
        
        # Mapear metodo_pago a tipo_pago (1=efectivo, 2=transferencia, 3=tarjeta)
        tipo_pago_map = {
            "efectivo": 1,
            "transferencia": 2,
            "tarjeta": 3
        }
        
        pago_request_data = PagoSchemaRequest(
            id_accion=accion_creada.id_accion,
            monto=pago_data["total_pago"],
            tipo_pago=tipo_pago_map.get(pago_data["metodo_pago"], 2),  # Por defecto transferencia
            estado_pago=2,  # Pagado
            observaciones=f"Pago simulado - Referencia: {referencia_temporal}"
        )
        
        pago_creado = pago_repository.create_pago(pago_request_data)
        
        # Generar certificado
        socio_repository = SocioRepository()
        socio = socio_repository.get_socio(accion_creada.id_socio)
        socio_titular_nombre = f"{socio.nombres} {socio.apellidos}" if socio else f"Socio {accion_creada.id_socio}"

        certificado_data = {
            'id_accion': accion_creada.id_accion,
            'id_socio': accion_creada.id_socio,
            'tipo_accion': accion_creada.tipo_accion,
            'cantidad_acciones': accion_creada.cantidad_acciones,
            'precio_unitario': accion_creada.precio_unitario,
            'total_pago': accion_creada.total_pago,
            'metodo_pago': accion_creada.metodo_pago,
            'socio_titular': socio_titular_nombre,
            'modalidad_pago_info': f"Modalidad {accion_creada.modalidad_pago}"
        }
        
        # Generar certificado completo (original + cifrado)
        certificado_info = certificate_service.generar_certificado_completo(certificado_data, accion_creada.id_socio)
        
        # Actualizar acción con certificado
        accion_repository.update_accion(accion_creada.id_accion, {
            "certificado_pdf": certificado_info["certificado_original"],
            "certificado_cifrado": True,
            "fecha_emision_certificado": datetime.now().isoformat()
        })
        
        # Limpiar pago temporal
        temp_payment_service.delete_temp_payment(referencia_temporal)
        
        return {
            "mensaje": "Pago confirmado y acción creada exitosamente",
            "accion": {
                "id_accion": accion_creada.id_accion,
                "id_socio": accion_creada.id_socio,
                "cantidad_acciones": accion_creada.cantidad_acciones,
                "precio_unitario": accion_creada.precio_unitario,
                "total_pago": accion_creada.total_pago,
                "metodo_pago": accion_creada.metodo_pago,
                "estado_accion": 2,
                "estado_nombre": "Aprobada",
                "fecha_creacion": datetime.now().isoformat()
            },
            "pago": {
                "id_pago": pago_creado.id_pago,
                "id_accion": pago_creado.id_accion,
                "monto": pago_creado.monto,
                "tipo_pago": pago_creado.tipo_pago,
                "estado_pago": pago_creado.estado_pago,
                "fecha_pago": pago_creado.fecha_de_pago,
                "observaciones": pago_creado.observaciones
            },
            "certificado": {
                "disponible": True,
                "ruta": certificado_info["certificado_original"],
                "fecha_generacion": certificado_info["fecha_generacion"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirmando pago: {str(e)}")

@router.get("/simular-pago/estado/{referencia_temporal}")
def obtener_estado_pago_simulado(referencia_temporal: str, current_user=Depends(get_current_user)):
    """
    Obtiene el estado de un pago simulado
    """
    try:
        temp_payment_service = TempPaymentService()
        payment_data = temp_payment_service.get_temp_payment(referencia_temporal)
        
        if not payment_data:
            raise HTTPException(status_code=404, detail="Pago temporal no encontrado o expirado")
        
        # Extraer datos del pago (están en datos_pago)
        pago_data = payment_data.get("datos_pago", payment_data)
        
        return {
            "referencia_temporal": referencia_temporal,
            "estado": payment_data["estado"],
            "fecha_creacion": payment_data["fecha_creacion"],
            "fecha_expiracion": payment_data["fecha_limite"],  # Usar fecha_limite en lugar de fecha_expiracion
            "pago_info": {
                "id_socio": pago_data["id_socio"],
                "cantidad_acciones": pago_data["cantidad_acciones"],
                "precio_unitario": pago_data["precio_unitario"],
                "total_pago": pago_data["total_pago"],
                "metodo_pago": pago_data["metodo_pago"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado del pago: {str(e)}")

@router.get("/simular-pago/pagos-temporales")
def listar_pagos_temporales(current_user=Depends(get_current_user)):
    """
    Lista todos los pagos temporales (solo administradores)
    """
    try:
        # Verificar que es administrador
        if current_user["rol"] != 1:
            raise HTTPException(status_code=403, detail="Solo administradores pueden ver pagos temporales")
        
        temp_payment_service = TempPaymentService()
        pagos = temp_payment_service.get_all_temp_payments()
        
        return {
            "pagos_temporales": pagos,
            "total": len(pagos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando pagos temporales: {str(e)}")

@router.delete("/simular-pago/limpiar-pagos")
def limpiar_pagos_temporales(current_user=Depends(get_current_user)):
    """
    Limpia pagos temporales expirados (solo administradores)
    """
    try:
        # Verificar que es administrador
        if current_user["rol"] != 1:
            raise HTTPException(status_code=403, detail="Solo administradores pueden limpiar pagos temporales")
        
        temp_payment_service = TempPaymentService()
        temp_payment_service.cleanup_expired_payments()
        
        return {
            "mensaje": "Pagos temporales expirados limpiados exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando pagos temporales: {str(e)}")

# ==================== ENDPOINTS PARA PAGO SIMULADO (SIN SERVICIOS EXTERNOS) ==================== 