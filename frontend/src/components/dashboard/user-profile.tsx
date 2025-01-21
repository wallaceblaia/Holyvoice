"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar"
import { AvatarSelector } from "./avatar-selector"

type UserData = {
  name: string
  email: string
  avatar?: string
  is_superuser: boolean
  last_login: string | null
}

function getUserType(is_superuser: boolean) {
  return is_superuser ? "Administrador" : "Usuário"
}

function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

export function UserProfile() {
  const router = useRouter()
  const [userData, setUserData] = useState<UserData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const handleAvatarSelect = async (avatarUrl: string) => {
    if (!userData) return

    try {
      const response = await fetch("http://localhost:8000/api/v1/users/me", {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "text/plain",
        },
        body: avatarUrl,
      })

      if (response.ok) {
        const updatedUser = await response.json()
        setUserData(updatedUser)
      } else {
        console.error("Erro ao atualizar avatar:", await response.text())
      }
    } catch (error) {
      console.error("Erro ao atualizar avatar:", error)
    }
  }

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token")
      
      if (!token) {
        router.push("/auth/login")
        return
      }

      try {
        const response = await fetch("http://localhost:8000/api/v1/users/me", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          credentials: "include",
        })

        if (response.ok) {
          const data = await response.json()
          setUserData(data)
        } else if (response.status === 401) {
          // Se o token estiver inválido/expirado
          localStorage.removeItem("token")
          router.push("/auth/login")
        } else {
          console.error("Erro ao buscar dados do usuário:", await response.text())
        }
      } catch (error) {
        console.error("Erro ao buscar dados do usuário:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserData()
  }, [router])

  if (isLoading) {
    return <div>Carregando...</div>
  }

  if (!userData) {
    return <div>Erro ao carregar dados do usuário</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="space-y-4">
          <Avatar className="h-20 w-20">
            {userData.avatar ? (
              <AvatarImage src={userData.avatar} alt={userData.name} />
            ) : (
              <AvatarFallback>{getInitials(userData.name)}</AvatarFallback>
            )}
          </Avatar>
          <AvatarSelector 
            currentAvatar={userData.avatar} 
            onSelect={handleAvatarSelect}
            userName={userData.name}
          />
        </div>
        <div>
          <h2 className="text-2xl font-bold">{userData.name}</h2>
          <p className="text-muted-foreground">{userData.email}</p>
        </div>
      </div>
      <div className="grid gap-4">
        <div className="space-y-2">
          <h3 className="font-medium">Tipo de Usuário</h3>
          <p className="text-muted-foreground">{getUserType(userData.is_superuser)}</p>
        </div>
        <div className="space-y-2">
          <h3 className="font-medium">Último Acesso</h3>
          <p className="text-muted-foreground">
            {userData.last_login 
              ? new Date(userData.last_login).toLocaleString('pt-BR')
              : "Primeiro acesso"}
          </p>
        </div>
      </div>
    </div>
  )
} 