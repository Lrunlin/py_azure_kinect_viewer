import route from "./router.tsx";
import { useRoutes } from "react-router-dom";

function App() {
  let Element = useRoutes(route);
  return <>{Element}</>;
}

export default App;
