import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"

import { type SiteCreate, SitesService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
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
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddSite = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<SiteCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      domain: "",
      name: "",
      frontend_domain: "",
      is_active: true,
      is_default: false,
      settings: null,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: SiteCreate) =>
      SitesService.createSite({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Site created successfully.")
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

  const onSubmit: SubmitHandler<SiteCreate> = (data) => {
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
        <Button value="add-site" my={4}>
          <FaPlus fontSize="16px" />
          Add Site
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add Site</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new site.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Site Name"
              >
                <Input
                  {...register("name", {
                    required: "Site name is required.",
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
                    required: "Backend domain is required.",
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
                    required: "Frontend domain is required.",
                  })}
                  placeholder="example.com or localhost:5173"
                  type="text"
                />
              </Field>

              <Checkbox {...register("is_active")} defaultChecked>
                Active
              </Checkbox>

              <Checkbox {...register("is_default")}>Default Site</Checkbox>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddSite
