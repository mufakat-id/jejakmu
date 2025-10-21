"use client"

import { toaster } from "@/components/ui/toaster"

const useCustomToast = () => {
  const showSuccessToast = (description: string) => {
    toaster.create({
      title: "Success!",
      description,
      type: "success",
    })
  }

  const showErrorToast = (description: string) => {
    toaster.create({
      title: "Something went wrong!",
      description,
      type: "error",
    })
  }

  const showWarningToast = (description: string) => {
    toaster.create({
      title: "Warning!",
      description,
      type: "warning",
    })
  }

  const showInfoToast = (description: string) => {
    toaster.create({
      title: "Info",
      description,
      type: "info",
    })
  }

  return { showSuccessToast, showErrorToast, showWarningToast, showInfoToast }
}

export default useCustomToast
