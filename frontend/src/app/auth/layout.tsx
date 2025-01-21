import { Metadata } from "next"

export const metadata: Metadata = {
  title: {
    default: "HolyVoice - Autenticação",
    template: "%s | HolyVoice"
  },
  description: "Autenticação para a plataforma HolyVoice",
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
} 