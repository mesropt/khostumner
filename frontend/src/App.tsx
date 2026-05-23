import { Routes, Route } from "react-router-dom"
import Layout from "@/components/Layout"
import HomePage from "@/pages/HomePage"
import NotFoundPage from "@/pages/NotFoundPage"
import PersonsPage from "@/pages/PersonsPage"
import PoliticianProfilePage from "@/pages/PoliticianProfilePage"
import PartyPage from "@/pages/PartyPage"
import ElectionsListPage from "@/pages/ElectionsListPage"
import ElectionDetailPage from "@/pages/ElectionDetailPage"
import PromisesListPage from "@/pages/PromisesListPage"
import FulfilledPage from "@/pages/FulfilledPage"
import UnfulfilledPage from "@/pages/UnfulfilledPage"
import PromiseDetailPage from "@/pages/PromiseDetailPage"
import AboutPage from "@/pages/AboutPage"

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/promises" element={<PromisesListPage />} />
        <Route path="/fulfilled" element={<FulfilledPage />} />
        <Route path="/unfulfilled" element={<UnfulfilledPage />} />
        <Route path="/promises/:slug" element={<PromiseDetailPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/persons" element={<PersonsPage />} />
        <Route path="/persons/:slug" element={<PoliticianProfilePage />} />
        <Route path="/parties/:slug" element={<PartyPage />} />
        <Route path="/elections" element={<ElectionsListPage />} />
        <Route path="/elections/:slug" element={<ElectionDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
