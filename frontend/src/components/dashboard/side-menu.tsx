"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils/index"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  ChevronLeft,
  Home,
  Music2,
  Users,
  Settings,
  Menu as MenuIcon
} from "lucide-react"

const menuItems = [
  {
    title: "Início",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Músicas",
    href: "/dashboard/songs",
    icon: Music2,
  },
  {
    title: "Usuários",
    href: "/dashboard/users",
    icon: Users,
  },
  {
    title: "Configurações",
    href: "/dashboard/settings",
    icon: Settings,
  },
]

export function SideMenu() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "relative h-full border-r bg-background p-4 transition-all duration-300",
        collapsed ? "w-[80px]" : "w-[240px]"
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className={cn(
          "text-lg font-semibold transition-all duration-300",
          collapsed ? "opacity-0 w-0" : "opacity-100"
        )}>
          HolyVoice
        </h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8 ml-auto"
        >
          {collapsed ? <MenuIcon size={18} /> : <ChevronLeft size={18} />}
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-8rem)]">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <Button
                variant={pathname === item.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  collapsed ? "px-2" : "px-4"
                )}
              >
                <item.icon size={20} className={cn(
                  "transition-colors",
                  pathname === item.href 
                    ? "text-primary" 
                    : "text-muted-foreground group-hover:text-primary"
                )} />
                <span className={cn(
                  "ml-2 transition-all duration-300",
                  collapsed ? "opacity-0 w-0" : "opacity-100"
                )}>
                  {item.title}
                </span>
              </Button>
            </Link>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
} 