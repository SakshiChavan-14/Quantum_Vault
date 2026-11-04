from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.health.router import router as health_router

# Initialize logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.exceptions import (
    AuthenticationError,
    InvalidCredentials,
    TokenExpired,
    UserAlreadyExists,
    UserNotFound,
    FolderNotFound,
    DuplicateFolderName,
    InvalidParentFolder,
    SystemFolderOperation,
    FolderCircularReference,
    FolderMoveNotAllowed,
    FileNotFound,
    FileSizeExceeded,
    InvalidFileType,
    StorageQuotaExceeded,
    FileAccessDenied,
    UploadFailed,
    FileAlreadyExists,
    InvalidFolder,
    EncryptionFailed,
    DecryptionFailed,
    FileDeletionFailed,
    FileIntegrityCompromised,
    UnsupportedEncryptionAlgorithm,
    MasterKeyConfigurationError,
    KeyProtectionError,
    UserKyberKeyUnavailable
)

# Exception Handlers
@app.exception_handler(UserAlreadyExists)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    logger.warning(f"UserAlreadyExists: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(UserNotFound)
async def user_not_found_handler(request: Request, exc: UserNotFound):
    logger.warning(f"UserNotFound: {exc}")
    return JSONResponse(status_code=404, content={"success": False, "message": str(exc)})

@app.exception_handler(InvalidCredentials)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    logger.warning(f"InvalidCredentials: {exc}")
    return JSONResponse(status_code=401, content={"success": False, "message": str(exc)})

@app.exception_handler(TokenExpired)
async def token_expired_handler(request: Request, exc: TokenExpired):
    logger.warning(f"TokenExpired: {exc}")
    return JSONResponse(status_code=401, content={"success": False, "message": str(exc)})

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    logger.warning(f"AuthenticationError: {exc}")
    return JSONResponse(status_code=401, content={"success": False, "message": str(exc)})

@app.exception_handler(FolderNotFound)
async def folder_not_found_handler(request: Request, exc: FolderNotFound):
    logger.warning(f"FolderNotFound: {exc}")
    return JSONResponse(status_code=404, content={"success": False, "message": str(exc)})

@app.exception_handler(DuplicateFolderName)
async def duplicate_folder_name_handler(request: Request, exc: DuplicateFolderName):
    logger.warning(f"DuplicateFolderName: {exc}")
    return JSONResponse(status_code=409, content={"success": False, "message": str(exc)})

@app.exception_handler(InvalidParentFolder)
async def invalid_parent_folder_handler(request: Request, exc: InvalidParentFolder):
    logger.warning(f"InvalidParentFolder: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(SystemFolderOperation)
async def system_folder_operation_handler(request: Request, exc: SystemFolderOperation):
    logger.warning(f"SystemFolderOperation: {exc}")
    return JSONResponse(status_code=403, content={"success": False, "message": str(exc)})

@app.exception_handler(FolderCircularReference)
async def folder_circular_reference_handler(request: Request, exc: FolderCircularReference):
    logger.warning(f"FolderCircularReference: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(FolderMoveNotAllowed)
async def folder_move_not_allowed_handler(request: Request, exc: FolderMoveNotAllowed):
    logger.warning(f"FolderMoveNotAllowed: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(FileNotFound)
async def file_not_found_handler(request: Request, exc: FileNotFound):
    logger.warning(f"FileNotFound: {exc}")
    return JSONResponse(status_code=404, content={"success": False, "message": str(exc)})

@app.exception_handler(FileSizeExceeded)
async def file_size_exceeded_handler(request: Request, exc: FileSizeExceeded):
    logger.warning(f"FileSizeExceeded: {exc}")
    return JSONResponse(status_code=413, content={"success": False, "message": str(exc)})

@app.exception_handler(InvalidFileType)
async def invalid_file_type_handler(request: Request, exc: InvalidFileType):
    logger.warning(f"InvalidFileType: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(StorageQuotaExceeded)
async def storage_quota_exceeded_handler(request: Request, exc: StorageQuotaExceeded):
    logger.warning(f"StorageQuotaExceeded: {exc}")
    return JSONResponse(status_code=413, content={"success": False, "message": str(exc)})

@app.exception_handler(FileAccessDenied)
async def file_access_denied_handler(request: Request, exc: FileAccessDenied):
    logger.warning(f"FileAccessDenied: {exc}")
    return JSONResponse(status_code=403, content={"success": False, "message": str(exc)})

@app.exception_handler(UploadFailed)
async def upload_failed_handler(request: Request, exc: UploadFailed):
    logger.error(f"UploadFailed: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(FileAlreadyExists)
async def file_already_exists_handler(request: Request, exc: FileAlreadyExists):
    logger.warning(f"FileAlreadyExists: {exc}")
    return JSONResponse(status_code=409, content={"success": False, "message": str(exc)})

@app.exception_handler(InvalidFolder)
async def invalid_folder_handler(request: Request, exc: InvalidFolder):
    logger.warning(f"InvalidFolder: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(EncryptionFailed)
async def encryption_failed_handler(request: Request, exc: EncryptionFailed):
    logger.error(f"EncryptionFailed: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "message": "Encryption failed"})

@app.exception_handler(DecryptionFailed)
async def decryption_failed_handler(request: Request, exc: DecryptionFailed):
    logger.error(f"DecryptionFailed: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "message": "Decryption failed"})

@app.exception_handler(FileDeletionFailed)
async def file_deletion_failed_handler(request: Request, exc: FileDeletionFailed):
    logger.error(f"FileDeletionFailed: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "message": "Deletion failed"})

@app.exception_handler(FileIntegrityCompromised)
async def file_integrity_compromised_handler(request: Request, exc: FileIntegrityCompromised):
    logger.error(f"SECURITY ALERT - FileIntegrityCompromised: {exc}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "File integrity verification failed: tampering detected"}
    )

@app.exception_handler(UnsupportedEncryptionAlgorithm)
async def unsupported_encryption_algorithm_handler(request: Request, exc: UnsupportedEncryptionAlgorithm):
    logger.error(f"UnsupportedEncryptionAlgorithm: {exc}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": str(exc)}
    )

@app.exception_handler(MasterKeyConfigurationError)
async def master_key_error_handler(request: Request, exc: MasterKeyConfigurationError):
    logger.error(f"MasterKeyConfigurationError: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "message": "Cryptographic configuration error"})

@app.exception_handler(KeyProtectionError)
async def key_protection_error_handler(request: Request, exc: KeyProtectionError):
    logger.error(f"KeyProtectionError: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "message": "Key protection operation failed"})

@app.exception_handler(UserKyberKeyUnavailable)
async def user_kyber_key_unavailable_handler(request: Request, exc: UserKyberKeyUnavailable):
    logger.warning(f"UserKyberKeyUnavailable: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An internal server error occurred."}
    )

from app.api.v1.auth.router import router as auth_router
from app.api.v1.dashboard.router import router as dashboard_router
from app.api.v1.folders.router import router as folders_router
from app.api.v1.files.router import router as files_router
from app.api.v1.audit.router import router as audit_router

# API Routers
app.include_router(health_router, prefix=f"{settings.API_V1_STR}/health", tags=["health"])
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(folders_router, prefix=f"{settings.API_V1_STR}/folders", tags=["folders"])
app.include_router(files_router, prefix=f"{settings.API_V1_STR}/files", tags=["files"])
app.include_router(audit_router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
