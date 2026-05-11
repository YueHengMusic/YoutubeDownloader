/* eslint-disable no-console */
/**
 * 图标生成脚本（单一源图 -> 多平台产物）
 *
 * 目标：
 * 1) 使用同一份 SVG 源图，生成 Windows/macOS/Linux 所需图标文件；
 * 2) 避免手工维护多份图标导致风格不一致；
 * 3) 保证打包图标（.exe/.app/AppImage）与运行时窗口图标一致。
 */
const fs = require("node:fs");
const path = require("node:path");
const sharp = require("sharp");
const png_to_ico = require("png-to-ico");
const { Icns, IcnsImage } = require("@fiahfy/icns");

const project_root = path.resolve(__dirname, "..");
const icon_dir = path.join(project_root, "resources", "icons");
const source_svg_path = path.join(icon_dir, "app_icon.svg");
const generated_dir = path.join(icon_dir, "generated");

/**
 * 需要输出的 PNG 尺寸：
 * - 同时服务于 ico/icns 组装；
 * - 也方便后续在 Linux/文档等场景直接复用。
 */
const png_sizes = [16, 24, 32, 48, 64, 128, 256, 512, 1024];

function ensure_dirs() {
  fs.mkdirSync(generated_dir, { recursive: true });
}

async function generate_png_variants() {
  const outputs = [];
  for (const size of png_sizes) {
    const output_path = path.join(generated_dir, `app_icon_${size}.png`);
    // 每个尺寸都从同一 SVG 直接缩放，避免连环缩放造成质量损失。
    await sharp(source_svg_path).resize(size, size).png().toFile(output_path);
    outputs.push({ size, output_path });
  }
  // 主 PNG 统一导出为 1024，供 Linux 与通用 icon 字段复用。
  const main_png_path = path.join(icon_dir, "app_icon.png");
  fs.copyFileSync(path.join(generated_dir, "app_icon_1024.png"), main_png_path);
  return outputs;
}

async function generate_ico(png_outputs) {
  /**
   * Windows ico 常用多尺寸组合：
   * 16/24/32/48/64/128/256
   */
  const ico_sources = png_outputs
    .filter((item) => [16, 24, 32, 48, 64, 128, 256].includes(item.size))
    .map((item) => item.output_path);
  const ico_buffer = await png_to_ico(ico_sources);
  fs.writeFileSync(path.join(icon_dir, "app_icon.ico"), ico_buffer);
}

function generate_icns(png_outputs) {
  /**
   * macOS icns 由多尺寸图像组成：
   * 16/32/64/128/256/512/1024
   */
  const icns = new Icns();
  /**
   * 显式指定 osType，避免库默认参数为空导致 “No supported osType”。
   * 这里采用 PNG 格式图块，兼容现代 macOS。
   */
  const icns_type_map = {
    16: "icp4",
    32: "icp5",
    64: "icp6",
    128: "ic07",
    256: "ic08",
    512: "ic09",
    1024: "ic10"
  };
  for (const source of png_outputs) {
    const os_type = icns_type_map[source.size];
    if (!os_type) continue;
    const png_buffer = fs.readFileSync(source.output_path);
    icns.append(IcnsImage.fromPNG(png_buffer, os_type));
  }
  fs.writeFileSync(path.join(icon_dir, "app_icon.icns"), icns.data);
}

async function main() {
  if (!fs.existsSync(source_svg_path)) {
    throw new Error(`图标源文件不存在: ${source_svg_path}`);
  }
  ensure_dirs();
  const png_outputs = await generate_png_variants();
  await generate_ico(png_outputs);
  generate_icns(png_outputs);
  console.log("图标生成完成: app_icon.png / app_icon.ico / app_icon.icns");
}

main().catch((error) => {
  console.error("图标生成失败:", error);
  process.exit(1);
});
