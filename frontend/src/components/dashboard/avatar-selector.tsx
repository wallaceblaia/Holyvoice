"use client"

import React, { Fragment } from "react"
import { Dialog, Transition } from "@headlessui/react"
import { Button } from "../ui/button"
import { Avatar, AvatarImage } from "../ui/avatar"

// Cores profissionais para os avatares
const colors = [
  "0A2647,144272", // Azul profundo
  "1B6B93,4FC0D0", // Azul corporativo
  "164B60,1B6B93", // Azul marinho
  "27374D,526D82", // Azul acinzentado
  "2C3333,2E4F4F", // Cinza elegante
  "1A120B,3C2A21", // Marrom executivo
  "635985,443C68", // Roxo sofisticado
  "4F4557,6D5D6E", // Roxo acinzentado
  "3F4E4F,2C3639", // Verde musgo
  "27374D,526D82", // Azul noturno
  "1F1717,CE5959", // Vermelho vinho
  "2D2727,413543"  // Preto elegante
]

type AvatarSelectorProps = {
  currentAvatar?: string
  onSelect: (avatarUrl: string) => void
  userName: string
}

function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

export function AvatarSelector({ currentAvatar, onSelect, userName }: AvatarSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const initials = getInitials(userName)

  // Gera URLs de avatar usando UI Avatars com cores personalizadas
  const avatars = colors.map((color, i) => ({
    id: i + 1,
    url: `https://ui-avatars.com/api/?background=${color.split(',')[0]}&color=ffffff&name=${initials}&bold=true&format=svg&size=128`,
  }))

  return (
    <>
      <Button variant="outline" onClick={() => setIsOpen(true)}>
        Alterar Avatar
      </Button>

      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-background p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 mb-4"
                  >
                    Escolha seu Avatar
                  </Dialog.Title>
                  <div className="mt-4 grid grid-cols-4 gap-4">
                    {avatars.map((avatar) => (
                      <button
                        key={avatar.id}
                        className={`rounded-lg p-1 hover:bg-accent transition-all duration-200 ${
                          currentAvatar === avatar.url ? "ring-2 ring-primary" : ""
                        }`}
                        onClick={() => {
                          onSelect(avatar.url)
                          setIsOpen(false)
                        }}
                      >
                        <Avatar className="h-16 w-16">
                          <AvatarImage src={avatar.url} alt={`Avatar ${avatar.id}`} />
                        </Avatar>
                      </button>
                    ))}
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  )
} 