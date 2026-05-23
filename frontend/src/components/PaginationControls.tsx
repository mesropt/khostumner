import { useSearchParams } from "react-router-dom"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

interface PaginationControlsProps {
  currentPage: number
  totalPages: number
  pageParamKey?: string
}

export default function PaginationControls({
  currentPage,
  totalPages,
  pageParamKey = "page",
}: PaginationControlsProps) {
  const [, setSearchParams] = useSearchParams()

  function goToPage(p: number) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.set(pageParamKey, String(p))
      return next
    })
  }

  if (totalPages <= 1) return null

  // Build page numbers to display
  let pageNumbers: (number | "ellipsis")[]
  if (totalPages <= 7) {
    pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)
  } else {
    pageNumbers = [1, 2, 3, "ellipsis", totalPages - 2, totalPages - 1, totalPages]
  }

  return (
    <div className="flex justify-center mt-6">
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={(e) => {
                e.preventDefault()
                if (currentPage > 1) goToPage(currentPage - 1)
              }}
              aria-disabled={currentPage <= 1}
              className={currentPage <= 1 ? "pointer-events-none opacity-50" : ""}
            />
          </PaginationItem>

          {pageNumbers.map((page, idx) =>
            page === "ellipsis" ? (
              <PaginationItem key={`ellipsis-${idx}`}>
                <PaginationEllipsis />
              </PaginationItem>
            ) : (
              <PaginationItem key={page}>
                <PaginationLink
                  href="#"
                  isActive={page === currentPage}
                  onClick={(e) => {
                    e.preventDefault()
                    goToPage(page)
                  }}
                >
                  {page}
                </PaginationLink>
              </PaginationItem>
            )
          )}

          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={(e) => {
                e.preventDefault()
                if (currentPage < totalPages) goToPage(currentPage + 1)
              }}
              aria-disabled={currentPage >= totalPages}
              className={currentPage >= totalPages ? "pointer-events-none opacity-50" : ""}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  )
}
