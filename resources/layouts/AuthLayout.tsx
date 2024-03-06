import { Helmet, HelmetProvider } from "react-helmet-async"
import favicon from "@/assets/favicon.png"
interface AuthLayoutProps {
  children: React.ReactNode
  title: string
  description: string
  keywords: string
}

const helmetContext = {}

const AuthLayout = ({
  children,
  title,
  description,
  keywords,
}: AuthLayoutProps) => {
  return (
    <HelmetProvider context={helmetContext}>
      <Helmet>
        <meta charSet="utf-8" />
        <meta name="description" content={description} />
        <meta name="keywords" content={keywords} />
        <link rel="icon" type="image/x-icon" href={favicon} />
        <title>{title}</title>
      </Helmet>
      {children}
    </HelmetProvider>
  )
}

AuthLayout.defaultProps = {
  title: "Litestar Fullstack Application",
  description: "A fullstack reference application",
  keywords: "litestar",
}

export default AuthLayout
