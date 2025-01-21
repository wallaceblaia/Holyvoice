import { Metadata } from "next"
import Image from "next/image"
import Link from "next/link"
import { UserAuthForm } from "@/components/auth/user-auth-form"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

export const metadata: Metadata = {
  title: "Login | HolyVoice",
  description: "Faça login para acessar o sistema HolyVoice",
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      <div className="container relative h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0">
        <Link
          href="/auth/register"
          className={cn(
            buttonVariants({ variant: "ghost", size: "sm" }),
            "absolute right-4 top-4 md:right-8 md:top-8 font-medium"
          )}
        >
          Criar Conta
        </Link>
        <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-600" />
          <div className="relative z-20 flex items-center text-lg font-bold">
            <Image
              src="/logo.svg"
              alt="HolyVoice Logo"
              width={40}
              height={40}
              className="mr-2 dark:invert"
            />
            HolyVoice
          </div>
          <div className="relative z-20 mt-auto">
            <blockquote className="space-y-2">
              <p className="text-lg">
                Transforme seu conteúdo audiovisual com nossa plataforma integrada de processamento,
                transcrição e tradução de vídeos.
              </p>
              <footer className="text-sm text-white/80">
                Tecnologia de ponta para suas necessidades de mídia
              </footer>
            </blockquote>
          </div>
        </div>
        <div className="lg:p-8">
          <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
            <div className="flex flex-col space-y-2 text-center">
              <h1 className="text-2xl font-semibold tracking-tight">
                Bem-vindo de volta
              </h1>
              <p className="text-sm text-muted-foreground">
                Entre com seu email e senha para acessar sua conta
              </p>
            </div>
            <UserAuthForm type="login" />
            <div className="flex flex-col space-y-2 text-center text-sm">
              <Link
                href="/auth/forgot-password"
                className="text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
              >
                Esqueceu sua senha?
              </Link>
              <p className="text-muted-foreground">
                Novo por aqui?{" "}
                <Link
                  href="/auth/register"
                  className="text-primary underline-offset-4 hover:underline"
                >
                  Crie sua conta
                </Link>
              </p>
            </div>
            <p className="px-8 text-center text-sm text-muted-foreground">
              <Link href="/auth/register" className="hover:text-brand underline underline-offset-4">
                Não tem uma conta? Crie agora
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 