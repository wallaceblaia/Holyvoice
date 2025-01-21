import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "HolyVoice",
  description: "Plataforma de gerenciamento de músicas para igrejas",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className="dark">
      <body className={`${inter.className} antialiased bg-background`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}