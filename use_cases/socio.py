from infrastructure.socio_repository import SocioRepository
from infrastructure.user_repository import UserRepository
from infrastructure.security import hash_password
from schemas.socio import SocioRequest, SocioResponse, SocioUpdateRequest
from fastapi import HTTPException
from typing import List
import logging

class SocioUseCase:
    def __init__(self, socio_repository: SocioRepository):
        self.socio_repository = socio_repository
        self.user_repository = UserRepository()

    def list_socios(self) -> List[SocioResponse]:
        socios = self.socio_repository.list_socios()
        return [SocioResponse(**socio.__dict__) for socio in socios]

    def get_socio(self, socio_id: int) -> SocioResponse:
        socio = self.socio_repository.get_socio(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return SocioResponse(**socio.__dict__)

    def create_socio(self, data: SocioRequest) -> SocioResponse:
        """
        Crea un socio y automáticamente crea un usuario asociado para que pueda hacer login.
        La contraseña será el CI_NIT del socio.
        
        Campos fijos:
        - id_club: siempre 1
        - estado: siempre 2  
        - tipo_membresia: siempre "accionista"
        """
        try:
            # Asegurar valores fijos independientemente de lo que envíe el frontend
            data.id_club = 1
            data.estado = 2
            data.tipo_membresia = "accionista"
            
            # 1. Crear el socio primero
            socio = self.socio_repository.create_socio(data)
            logging.info(f"Socio creado con ID: {socio.id_socio}")
            
            # 2. Generar nombre de usuario único
            username = self._generate_username(socio.nombres, socio.apellidos, socio.ci_nit)
            
            # 3. Verificar que el username no exista, si existe agregar el ID del socio
            original_username = username
            counter = 1
            while self.user_repository.get_by_username(username):
                username = f"{original_username}{socio.id_socio}"
                counter += 1
            
            # 4. Verificar que el email no esté en uso
            if self.user_repository.get_by_email(socio.correo_electronico):
                raise HTTPException(
                    status_code=400, 
                    detail=f"El correo electrónico {socio.correo_electronico} ya está registrado"
                )
            
            # 5. Crear usuario con contraseña = CI_NIT
            hashed_password = hash_password(socio.ci_nit)
            user = self.user_repository.create_user(
                nombre_usuario=username,
                contrasena_hash=hashed_password,
                rol=4,  # Rol: usuario (socio)
                estado='activo',
                id_club=socio.id_club,
                correo_electronico=socio.correo_electronico
            )
            logging.info(f"Usuario creado con ID: {user.id_usuario}, username: {username}")
            
            # 6. Actualizar el socio con el id_usuario
            from schemas.socio import SocioUpdateRequest
            update_data = SocioUpdateRequest(
                id_club=socio.id_club,
                nombres=socio.nombres,
                apellidos=socio.apellidos,
                ci_nit=socio.ci_nit,
                telefono=socio.telefono,
                correo_electronico=socio.correo_electronico,
                direccion=socio.direccion,
                estado=socio.estado,
                fecha_nacimiento=socio.fecha_nacimiento,
                tipo_membresia=socio.tipo_membresia,
                id_usuario=user.id_usuario
            )
            socio_actualizado = self.socio_repository.update_socio(socio.id_socio, update_data)
            
            logging.info(f"Socio {socio.id_socio} asociado con usuario {user.id_usuario}")
            
            return SocioResponse(**socio_actualizado.__dict__)
            
        except Exception as e:
            logging.error(f"Error creando socio con usuario: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error creando socio: {str(e)}"
            )
    
    def _generate_username(self, nombres: str, apellidos: str, ci_nit: str) -> str:
        """
        Genera un nombre de usuario único basado en:
        - Primera letra del nombre
        - Primer apellido
        - Últimos 3 dígitos del CI
        """
        # Limpiar y procesar nombres
        nombre_parts = nombres.strip().split()
        apellido_parts = apellidos.strip().split()
        
        if not nombre_parts or not apellido_parts:
            raise ValueError("Nombres y apellidos son requeridos para generar username")
        
        # Crear username: primera letra del nombre + primer apellido + últimos 3 dígitos del CI
        first_letter = nombre_parts[0][0].lower()
        first_surname = apellido_parts[0].lower()
        ci_suffix = ci_nit[-3:] if len(ci_nit) >= 3 else ci_nit
        
        # Limpiar caracteres especiales del apellido
        import re
        first_surname = re.sub(r'[^a-zA-Záéíóúñü]', '', first_surname)
        
        username = f"{first_letter}{first_surname}{ci_suffix}"
        
        return username

    def update_socio(self, socio_id: int, data: SocioUpdateRequest) -> SocioResponse:
        socio = self.socio_repository.update_socio(socio_id, data)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return SocioResponse(**socio.__dict__)

    def delete_socio(self, socio_id: int) -> dict:
        success = self.socio_repository.delete_socio(socio_id)
        if not success:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return {"detail": "Socio eliminado correctamente"}

    def get_acciones(self, socio_id: int):
        # Placeholder: lógica real se implementará en el módulo de acciones
        return []

    def get_historial_pagos(self, socio_id: int):
        # Placeholder: lógica real se implementará en el módulo de pagos
        return [] 