#!/bin/bash

echo "🚀 Iniciando atualização do repositório GitHub..."

# Obtém a mensagem do commit como argumento
if [ -z "$1" ]
then
    echo "❌ Por favor, forneça uma mensagem para o commit."
    echo "Exemplo: ./update-github.sh \"sua mensagem aqui\""
    exit 1
fi

# Adiciona todas as alterações
echo "📦 Adicionando alterações..."
git add .

# Cria o commit com a mensagem fornecida
echo "💾 Criando commit..."
git commit -m "$1"

# Envia para o GitHub
echo "☁️ Enviando para o GitHub..."
git push origin main

echo "✅ Atualização concluída com sucesso!" 