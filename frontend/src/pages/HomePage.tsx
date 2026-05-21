import { useHealth } from "@/hooks/useHealth"

export default function HomePage() {
  const { status, isLoading, isError } = useHealth()

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Խոստումներ</h1>

      <div className="bg-white rounded-lg shadow p-6 w-full max-w-sm">
        <p className="text-sm font-medium text-gray-500 mb-2">API Status:</p>
        {isLoading && (
          <p className="text-gray-600">Բեռնվում է...</p>
        )}
        {isError && (
          <p className="text-red-600 font-medium">Սխալ</p>
        )}
        {!isLoading && !isError && status !== null && (
          <p className="text-green-600 font-medium">{status}</p>
        )}
      </div>
    </main>
  )
}
