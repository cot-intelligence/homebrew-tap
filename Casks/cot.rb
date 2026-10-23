cask "cot" do
  version "1.14.0"
  sha256 "ff9570cab903e8a52cfbc1389c42fb73f090e6e1f259911bf8c28408005e5733"

  url "https://github.com/cot-intelligence/cot/releases/download/v#{version}/cot_#{version}_aarch64.dmg"
  name "cot"
  desc "Self-hosted observability for AI coding agents"
  homepage "https://cot.run/"

  auto_updates true
  depends_on arch: :arm64
  depends_on :macos

  app "cot.app"
end
