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

  // Build page numbers to display using a window around the current page so that
  // no pages are silently unreachable. Pages 1 and totalPages are always shown;
  // a window of ±1 around currentPage fills the middle (WR-07).
  let pageNumbers: (number | "ellipsis")[]
  if (totalPages <= 5) {
    pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)
  } else {
    const near = [currentPage - 1, currentPage, currentPage + 1].filter(
      (p) => p > 1 && p < totalPages
    )
    pageNumbers = [
      1,
      ...(near.length > 0 && near[0] > 2 ? (["ellipsis"] as const) : []),
      ...near,
      ...(near.length > 0 && near[near.length - 1] < totalPages - 1
        ? (["ellipsis"] as const)
        : []),
      totalPages,
    ]
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
