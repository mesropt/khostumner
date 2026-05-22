interface AvatarProps {
  photoUrl: string | null
  nameHy: string
  size?: "sm" | "md" | "lg"
}

function getInitials(nameHy: string): string {
  const parts = nameHy.trim().split(/\s+/)
  if (parts.length === 0 || parts[0] === "") return "?"
  const first = parts[0].charAt(0)
  const last = parts.length > 1 ? parts[parts.length - 1].charAt(0) : ""
  return first + last
}

const SIZE_CLASSES = {
  sm: "w-8 h-8 text-xs",
  md: "w-16 h-16 text-sm",
  lg: "w-24 h-24 text-lg",
}

export default function Avatar({ photoUrl, nameHy, size = "md" }: AvatarProps) {
  const sizeClass = SIZE_CLASSES[size]

  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={nameHy}
        className={`${sizeClass} rounded-full object-cover`}
      />
    )
  }

  return (
    <div
      className={`${sizeClass} flex items-center justify-center rounded-full bg-zinc-200 text-zinc-700 font-semibold`}
    >
      {getInitials(nameHy)}
    </div>
  )
}
