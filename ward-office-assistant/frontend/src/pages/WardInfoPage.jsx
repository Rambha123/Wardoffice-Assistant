export default function WardInfoPage() {
  // TODO: fetch from GET /api/services/office-info once that backend route
  // + OfficeInfo/Notice/FAQ CRUD exists. Hardcoded placeholder layout below
  // shows the intended sections.

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-semibold">Ward Office Information</h1>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Office Hours & Contact</h2>
        <p className="text-gray-500 text-sm">TODO: office_hours, phone, email from OfficeInfo</p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Departments</h2>
        <p className="text-gray-500 text-sm">TODO: list departments + responsible officers</p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Map</h2>
        <p className="text-gray-500 text-sm">TODO: embed map_embed_url in an &lt;iframe&gt;</p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Notices</h2>
        <p className="text-gray-500 text-sm">TODO: list Notice rows, most recent first</p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Frequently Asked Questions</h2>
        <p className="text-gray-500 text-sm">TODO: list FAQ rows, optionally grouped by service</p>
      </section>
    </div>
  );
}
