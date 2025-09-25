from infrastructure.accion_repository import AccionRepository
from schemas.accion import AccionRequest, AccionResponse, AccionUpdateRequest
from fastapi import HTTPException
from typing import List

class AccionUseCase:
    def __init__(self, accion_repository: AccionRepository):
        self.accion_repository = accion_repository

    def list_acciones(self) -> List[AccionResponse]:
        acciones = self.accion_repository.list_acciones()
        acciones_con_estado = []
        
        for accion in acciones:
            try:
                # Obtener modalidad de pago
                modalidad = self.accion_repository.get_modalidad_pago(accion.modalidad_pago)
                # Obtener estado de acción
                estado_accion = self.accion_repository.get_estado_accion(accion.estado_accion)
                # Obtener pagos realizados
                pagos_realizados = self.accion_repository.get_pagos(accion.id_accion)
                
                if modalidad:
                    # Calcular estado completo de pagos
                    estado_pagos = self.accion_repository.calcular_estado_pagos(accion, modalidad, pagos_realizados)
                    
                    # Crear respuesta con toda la información
                    accion_response = AccionResponse(**accion.__dict__).dict()
                    accion_response.update({
                        "estado_accion_info": {
                            "id": estado_accion["id_estado_accion"] if estado_accion else accion.estado_accion,
                            "nombre": estado_accion["nombre_estado_accion"] if estado_accion else "Desconocido"
                        } if estado_accion else {
                            "id": accion.estado_accion,
                            "nombre": "Desconocido"
                        },
                        "estado_pagos": {
                            "estado_pago": estado_pagos["estado_pago"],
                            "porcentaje_pagado": estado_pagos["porcentaje_pagado"],
                            "saldo_pendiente": estado_pagos["saldo_pendiente"],
                            "pagos_restantes": estado_pagos["pagos_restantes"],
                            "precio_inicial": estado_pagos["precio_inicial"],
                            "costo_renovacion_mensual": estado_pagos["costo_renovacion_mensual"],
                            "total_pagado": estado_pagos["total_pagado"],
                            "pagos_realizados": estado_pagos["pagos_realizados"],
                            "renovar": estado_pagos["renovar"]
                        },
                        "modalidad_pago_info": {
                            "descripcion": modalidad["descripcion"],
                            "meses_de_gracia": modalidad["meses_de_gracia"],
                            "porcentaje_renovacion_inicial": modalidad["porcentaje_renovacion_inicial"],
                            "porcentaje_renovacion_mensual": modalidad["porcentaje_renovacion_mensual"],
                            "costo_renovacion_estandar": modalidad["costo_renovacion_estandar"],
                            "cantidad_cuotas": modalidad["cantidad_cuotas"]
                        }
                    })
                    acciones_con_estado.append(accion_response)
                else:
                    # Si no hay modalidad, agregar con valores por defecto
                    accion_response = AccionResponse(**accion.__dict__).dict()
                    accion_response.update({
                        "estado_accion_info": {
                            "id": estado_accion["id_estado_accion"] if estado_accion else accion.estado_accion,
                            "nombre": estado_accion["nombre_estado_accion"] if estado_accion else "Desconocido"
                        } if estado_accion else {
                            "id": accion.estado_accion,
                            "nombre": "Desconocido"
                        },
                        "estado_pagos": {
                            "estado_pago": "MODALIDAD_NO_ENCONTRADA",
                            "porcentaje_pagado": 0,
                            "saldo_pendiente": 0,
                            "pagos_restantes": 0,
                            "precio_inicial": 0,
                            "costo_renovacion_mensual": 0,
                            "total_pagado": 0,
                            "pagos_realizados": 0,
                            "renovar": False
                        },
                        "modalidad_pago_info": {
                            "descripcion": "No encontrada",
                            "meses_de_gracia": 0,
                            "porcentaje_renovacion_inicial": 0,
                            "porcentaje_renovacion_mensual": 0,
                            "costo_renovacion_estandar": 0,
                            "cantidad_cuotas": 1
                        }
                    })
                    acciones_con_estado.append(accion_response)
                    
            except Exception as e:
                # Si hay error, agregar con estado de error
                accion_response = AccionResponse(**accion.__dict__).dict()
                accion_response.update({
                    "estado_accion_info": {
                        "id": accion.estado_accion,
                        "nombre": "Error"
                    },
                    "estado_pagos": {
                        "estado_pago": "ERROR_CALCULO",
                        "porcentaje_pagado": 0,
                        "saldo_pendiente": 0,
                        "pagos_restantes": 0,
                        "precio_inicial": 0,
                        "costo_renovacion_mensual": 0,
                        "total_pagado": 0,
                        "pagos_realizados": 0,
                        "renovar": False
                    },
                    "modalidad_pago_info": {
                        "descripcion": "Error",
                        "meses_de_gracia": 0,
                        "porcentaje_renovacion_inicial": 0,
                        "porcentaje_renovacion_mensual": 0,
                        "costo_renovacion_estandar": 0,
                        "cantidad_cuotas": 1
                    }
                })
                acciones_con_estado.append(accion_response)
        
        return acciones_con_estado

    def get_accion(self, accion_id: int) -> AccionResponse:
        accion = self.accion_repository.get_accion(accion_id)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return AccionResponse(**accion.__dict__)

    def create_accion(self, data: AccionRequest) -> AccionResponse:
        accion = self.accion_repository.create_accion(data)
        return AccionResponse(**accion.__dict__)

    def update_accion(self, accion_id: int, data: AccionUpdateRequest) -> AccionResponse:
        accion = self.accion_repository.update_accion(accion_id, data)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return AccionResponse(**accion.__dict__)

    def delete_accion(self, accion_id: int) -> dict:
        success = self.accion_repository.delete_accion(accion_id)
        if not success:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return {"detail": "Acción eliminada correctamente"}

    def generar_certificado(self, accion_id: int):
        """Genera un certificado PDF para una acción específica"""
        # Obtener datos de la acción
        accion = self.accion_repository.get_accion(accion_id)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        # Obtener datos del socio
        socio = self.accion_repository.get_socio_by_id(accion.id_socio)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        
        # Obtener modalidad de pago
        modalidad = self.accion_repository.get_modalidad_pago(accion.modalidad_pago)
        if not modalidad:
            raise HTTPException(status_code=404, detail="Modalidad de pago no encontrada")
        
        # Calcular estado de pagos para obtener precio_renovacion
        pagos_realizados = self.accion_repository.get_pagos(accion_id)
        estado_pagos = self.accion_repository.calcular_estado_pagos(accion, modalidad, pagos_realizados)
        
        # Generar PDF usando el servicio
        from infrastructure.pdf_service import PDFService
        pdf_service = PDFService()
        
        # Preparar datos para el PDF
        accion_data = {
            'id_accion': accion.id_accion,
            'id_socio': accion.id_socio,
            'tipo_accion': accion.tipo_accion,
            'fecha_emision_certificado': accion.fecha_emision_certificado
        }
        
        socio_data = {
            'nombre': socio.get('nombres', ''),
            'apellido': socio.get('apellidos', ''),
            'ci_nit': socio.get('ci_nit')
        }
        
        modalidad_data = {
            'precio_renovacion': estado_pagos['precio_renovacion']
        }
        
        # Generar PDF (ahora viene cifrado)
        resultado_pdf = pdf_service.generar_certificado_accion(accion_data, socio_data, modalidad_data)
        
        # Si el PDF viene cifrado, retornar con información de cifrado
        if isinstance(resultado_pdf, dict) and 'pdf_cifrado' in resultado_pdf:
            return resultado_pdf
        else:
            # Fallback: PDF sin cifrar
            return {
                "detail": "Certificado generado exitosamente (sin cifrar)",
                "pdf_content": resultado_pdf,
                "filename": f"certificado_accion_{accion_id}.pdf"
            }

    def ver_certificado(self, accion_id: int):
        # Placeholder
        return {"detail": "Descarga de certificado (placeholder)"}

    def cifrar_certificado(self, accion_id: int):
        # Placeholder
        return {"detail": "Certificado cifrado (placeholder)"}
    
    def descifrar_certificado(self, accion_id: int, password: str):
        """Descifra un certificado PDF con la contraseña proporcionada"""
        try:
            # Obtener datos de la acción
            accion = self.accion_repository.get_accion(accion_id)
            if not accion:
                raise HTTPException(status_code=404, detail="Acción no encontrada")
            
            # Obtener el PDF cifrado (esto requeriría almacenar el PDF en la BD)
            # Por ahora, vamos a generar el PDF y descifrarlo
            from infrastructure.pdf_service import PDFService
            pdf_service = PDFService()
            
            # Obtener datos del socio
            socio = self.accion_repository.get_socio_by_id(accion.id_socio)
            if not socio:
                raise HTTPException(status_code=404, detail="Socio no encontrado")
            
            # Obtener modalidad de pago
            modalidad = self.accion_repository.get_modalidad_pago(accion.modalidad_pago)
            if not modalidad:
                raise HTTPException(status_code=404, detail="Modalidad de pago no encontrada")
            
            # Calcular estado de pagos
            pagos_realizados = self.accion_repository.get_pagos(accion_id)
            estado_pagos = self.accion_repository.calcular_estado_pagos(accion, modalidad, pagos_realizados)
            
            # Preparar datos para el PDF
            accion_data = {
                'id_accion': accion.id_accion,
                'id_socio': accion.id_socio,
                'tipo_accion': accion.tipo_accion,
                'fecha_emision_certificado': accion.fecha_emision_certificado
            }
            
            socio_data = {
                'nombre': socio.get('nombres', ''),
                'apellido': socio.get('apellidos', ''),
                'ci_nit': socio.get('ci_nit')
            }
            
            modalidad_data = {
                'precio_renovacion': estado_pagos['precio_renovacion']
            }
            
            # Generar PDF cifrado
            resultado_pdf = pdf_service.generar_certificado_accion(accion_data, socio_data, modalidad_data)
            
            if isinstance(resultado_pdf, dict) and 'pdf_cifrado' in resultado_pdf:
                # Descifrar el PDF
                pdf_descifrado = pdf_service.descifrar_pdf(resultado_pdf['pdf_cifrado'], password)
                return pdf_descifrado
            else:
                # PDF sin cifrar
                return resultado_pdf
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error descifrando certificado: {str(e)}")

    def get_pagos(self, accion_id: int):
        # Placeholder
        return []

    def get_estado_pagos(self, accion_id: int):
        """Calcula el estado completo de pagos de una acción"""
        accion = self.accion_repository.get_accion(accion_id)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        
        # Obtener modalidad de pago
        modalidad = self.accion_repository.get_modalidad_pago(accion.modalidad_pago)
        if not modalidad:
            raise HTTPException(status_code=404, detail="Modalidad de pago no encontrada")
        
        # Obtener pagos realizados
        pagos_realizados = self.accion_repository.get_pagos(accion_id)
        
        # Calcular estado de pagos
        return self.accion_repository.calcular_estado_pagos(accion, modalidad, pagos_realizados)

    def list_acciones_con_estado_pagos(self):
        """Lista todas las acciones con estado de pagos resumido"""
        acciones = self.accion_repository.list_acciones()
        acciones_con_estado = []
        
        for accion in acciones:
            try:
                modalidad = self.accion_repository.get_modalidad_pago(accion.modalidad_pago)
                pagos_realizados = self.accion_repository.get_pagos(accion.id_accion)
                
                if modalidad:
                    estado_pagos = self.accion_repository.calcular_estado_pagos(accion, modalidad, pagos_realizados)
                    acciones_con_estado.append({
                        **AccionResponse(**accion.__dict__).dict(),
                        "estado_pagos": {
                            "estado_pago": estado_pagos["estado_pago"],
                            "porcentaje_pagado": estado_pagos["porcentaje_pagado"],
                            "saldo_pendiente": estado_pagos["saldo_pendiente"],
                            "pagos_restantes": estado_pagos["pagos_restantes"]
                        }
                    })
                else:
                    acciones_con_estado.append({
                        **AccionResponse(**accion.__dict__).dict(),
                        "estado_pagos": {
                            "estado_pago": "MODALIDAD_NO_ENCONTRADA",
                            "porcentaje_pagado": 0,
                            "saldo_pendiente": 0,
                            "pagos_restantes": 0
                        }
                    })
            except Exception as e:
                # Si hay error, agregar con estado de error
                acciones_con_estado.append({
                    **AccionResponse(**accion.__dict__).dict(),
                    "estado_pagos": {
                        "estado_pago": "ERROR_CALCULO",
                        "porcentaje_pagado": 0,
                        "saldo_pendiente": 0,
                        "pagos_restantes": 0
                    }
                })
        
        return acciones_con_estado 