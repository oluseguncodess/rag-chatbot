import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import Chatapp from "./components/chatapp";

const queryClient = new QueryClient();

export default function App() {
  return (
    <>
      <QueryClientProvider client={queryClient}>
        <Chatapp />
      </QueryClientProvider>
    </>
  );
}
