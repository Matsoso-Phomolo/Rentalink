export function LoadingState() {
  return <div className="data-state">Loading latest LineLink data...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="data-state error">{message}</div>;
}
