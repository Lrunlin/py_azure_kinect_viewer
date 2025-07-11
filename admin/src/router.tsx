import Index from "./pages/index.tsx";
import Show from "./pages/show.tsx";

const routes = [
  {
    path: "/",
    element: <Index />,
  },
  {
    path: "/show",
    element: <Show />,
  },
];

export default routes;
