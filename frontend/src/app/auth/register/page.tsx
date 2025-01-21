"use client"

import Link from "next/link"
import { UserAuthForm } from "@/components/auth/user-auth-form"

export default function RegisterPage() {
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">
            Criar uma conta
          </h1>
          <p className="text-sm text-muted-foreground">
            Preencha os dados abaixo para criar sua conta
          </p>
        </div>
        <UserAuthForm type="register" />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link href="/auth/login" className="hover:text-brand underline underline-offset-4">
            Já tem uma conta? Entre agora
          </Link>
        </p>
      </div>
    </div>
  )
} 