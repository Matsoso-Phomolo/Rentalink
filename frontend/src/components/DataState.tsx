export function LoadingState() {
  return <div className="data-state">Loading latest Rentalink data...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="data-state error">{message}</div>;
}
