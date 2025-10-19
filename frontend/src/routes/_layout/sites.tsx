import {
  Badge,
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { SitesService } from "@/client"
import { SiteActionsMenu } from "@/components/Common/SiteActionsMenu"
import PendingSites from "@/components/Pending/PendingSites"
import AddSite from "@/components/Sites/AddSite"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const sitesSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getSitesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      SitesService.readSites({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["sites", { page }],
  }
}

export const Route = createFileRoute("/_layout/sites")({
  component: Sites,
  validateSearch: (search) => sitesSearchSchema.parse(search),
})

function SitesTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getSitesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) => {
    navigate({
      to: "/sites",
      search: (prev) => ({ ...prev, page }),
    })
  }

  const sites = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingSites />
  }

  if (sites.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any sites yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new site to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Name</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Domain</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Frontend Domain</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {sites?.map((site) => (
            <Table.Row key={site.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {site.id}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {site.name}
                {site.is_default && (
                  <Badge ml={2} colorPalette="blue">
                    Default
                  </Badge>
                )}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {site.domain}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {site.frontend_domain}
              </Table.Cell>
              <Table.Cell>
                <Badge colorPalette={site.is_active ? "green" : "red"}>
                  {site.is_active ? "Active" : "Inactive"}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <SiteActionsMenu site={site} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Sites() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Sites Management
      </Heading>
      <AddSite />
      <SitesTable />
    </Container>
  )
}
