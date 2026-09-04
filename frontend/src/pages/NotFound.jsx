import { Link } from "react-router-dom";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-md text-center">
        <div className="mb-3 text-5xl">🧭</div>
        <h1 className="text-2xl font-bold">Page not found</h1>
        <p className="mt-2 text-sm text-white/50">The page you're looking for doesn't exist or has moved.</p>
        <Link to="/dashboard">
          <Button className="mt-6">Back to Dashboard</Button>
        </Link>
      </Card>
    </div>
  );
}
