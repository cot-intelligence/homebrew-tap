cask "cot" do
  version "1.13.3"
  sha256 "257dd06538181afee31661762f202aa20092d5988ca646fc1722ccfd05f0fa12"

  url "https://github.com/cot-intelligence/cot/releases/download/v#{version}/cot_#{version}_aarch64.dmg",
      verified: "github.com/cot-intelligence/cot/"
  name "cot"
  desc "Self-hosted observability for AI coding agents"
  homepage "https://cot.run/"

  auto_updates true
  depends_on arch: :arm64

  app "cot.app"
end
