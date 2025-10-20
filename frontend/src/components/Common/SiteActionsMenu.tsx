import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import type { SitePublic } from "@/client"
import DeleteSite from "../Sites/DeleteSite"
import EditSite from "../Sites/EditSite"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

interface SiteActionsMenuProps {
  site: SitePublic
}

export const SiteActionsMenu = ({ site }: SiteActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditSite site={site} />
        <DeleteSite id={site.id} />
      </MenuContent>
    </MenuRoot>
  )
}
