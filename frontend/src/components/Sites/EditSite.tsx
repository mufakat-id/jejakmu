import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type SitePublic, SitesService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditSiteProps {
  site: SitePublic
}

interface SiteUpdateForm {
  domain?: string
  name?: string
  frontend_domain?: string
  is_active?: boolean
  is_default?: boolean
  settings?: Record<string, unknown> | null
}

const EditSite = ({ site }: EditSiteProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SiteUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: site.name,
      domain: site.domain,
      frontend_domain: site.frontend_domain,
      is_active: site.is_active,
      is_default: site.is_default,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: SiteUpdateForm) =>
      SitesService.updateSite({ siteId: site.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Site updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["sites"] })
    },
  })

  const onSubmit: SubmitHandler<SiteUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit Site
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Site</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the site details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Site Name"
              >
                <Input
                  {...register("name", {
                    required: "Site name is required",
                  })}
                  placeholder="My Site"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.domain}
                errorText={errors.domain?.message}
                label="Backend Domain"
              >
                <Input
                  {...register("domain", {
                    required: "Backend domain is required",
                  })}
                  placeholder="api.example.com or localhost:8000"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.frontend_domain}
                errorText={errors.frontend_domain?.message}
                label="Frontend Domain"
              >
                <Input
                  {...register("frontend_domain", {
                    required: "Frontend domain is required",
                  })}
                  placeholder="example.com or localhost:5173"
                  type="text"
                />
              </Field>

              <Checkbox
                {...register("is_active")}
                defaultChecked={site.is_active}
              >
                Active
              </Checkbox>

              <Checkbox
                {...register("is_default")}
                defaultChecked={site.is_default}
              >
                Default Site
              </Checkbox>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditSite
