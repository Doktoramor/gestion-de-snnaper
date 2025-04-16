#!/bin/bash

# Verificar si es root
if [[ $EUID -ne 0 ]]; then
    echo "Este script requiere privilegios de administrador. Solicitando contraseña..."
    exec sudo "$0" "$@"
    exit
fi

# Nombre del perfil de Snapper (ajústalo si usas otro)
PROFILE="root"

function ver_instantaneas() {
    echo "Instantáneas disponibles:"
    snapper -c "$PROFILE" list
}

function crear_instantanea() {
    read -p "Introduce una descripción para la instantánea: " DESCRIPCION
    snapper -c "$PROFILE" create --description "$DESCRIPCION"
    echo "Instantánea creada con la descripción: $DESCRIPCION"
}

function restaurar_instantanea() {
    echo "Instantáneas disponibles:"
    snapper -c "$PROFILE" list
    echo
    read -p "Introduce el número de la instantánea que quieres restaurar (o presiona Enter para cancelar): " ID

    # Salir si no se introduce nada
    if [[ -z "$ID" ]]; then
        echo "Restauración cancelada."
        return
    fi

    # Permitir cancelar con 'q' o 'salir'
    if [[ "$ID" == "q" || "$ID" == "salir" ]]; then
        echo "Restauración cancelada."
        return
    fi

    echo "¡CUIDADO! Esto restaurará archivos a su estado anterior."
    read -p "¿Estás seguro? (s/n): " CONFIRMAR
    if [[ "$CONFIRMAR" == "s" || "$CONFIRMAR" == "S" ]]; then
        snapper -c "$PROFILE" undochange "$ID"
        echo "Instantánea $ID restaurada."
    else
        echo "Restauración cancelada."
    fi
}

while true; do
    clear
    echo "==== MENÚ DE SNAPSHOTS (SNAPPER) ===="
    echo "1) Ver instantáneas"
    echo "2) Crear una nueva instantánea"
    echo "3) Restaurar una instantánea"
    echo "4) Salir"
    echo "====================================="
    read -p "Selecciona una opción: " OPCION

    case $OPCION in
        1) ver_instantaneas ;;
        2) crear_instantanea ;;
        3) restaurar_instantanea ;;
        4) echo "¡Hasta luego!"; exit 0 ;;
        *) echo "Opción no válida." ;;
    esac
    echo ""
    read -p "Pulsa Enter para continuar..."
done
