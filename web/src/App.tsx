import { Navigate, Route, Routes } from "react-router-dom";
import { FaqAdmin } from "./features/faq/FaqAdmin";
import { HealthCheck } from "./features/health/HealthCheck";
import { Playground } from "./features/playground/Playground";
import { UnansweredAdmin } from "./features/unanswered/UnansweredAdmin";
import { VoicesAdmin } from "./features/voices/VoicesAdmin";
import { AppShell } from "./layout/AppShell";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Playground />} />
        <Route path="admin/faqs" element={<FaqAdmin />} />
        <Route path="admin/unanswered" element={<UnansweredAdmin />} />
        <Route path="admin/voices" element={<VoicesAdmin />} />
        <Route path="admin/health" element={<HealthCheck />} />
        <Route path="admin/playground" element={<Playground testMode />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
