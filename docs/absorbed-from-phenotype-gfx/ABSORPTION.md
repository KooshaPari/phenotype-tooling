# Absorbed from phenotype-gfx

**Source:** `KooshaPari/phenotype-gfx`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-gfx/`
**Tracked file count:** 257

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/workflows/ci.yml
    .gitignore
    Cargo.lock
    Cargo.toml
    README.md
    VERSION.toml
    benches/mesher_compare.rs
    benches/perf_suite.rs
    benches/post_stack_bench.rs
    benches/voxelizer_bench.rs
    bindings/c_api.rs
    docs/adr/ADR-004-single-core-ffi-edges.md
    examples/consume_mesh.rs
    findings/2026-06-16-terrain-block-c.md
    findings/2026-06-16-voxel-block-c.md
    findings/2026-06-16-water-block-c.md
    findings/2026-06-18-postfx-block-c.md
    findings/2026-06-18-sister-repo-block-c-summary.md
    spec/interop.md
    src/lib.rs
    src/lod.rs
    src/postfx/bloom_pass.rs
    src/postfx/error.rs
    src/postfx/mod.rs
    src/postfx/ports/lut_pipeline.rs
    src/postfx/ports/material_registry.rs
    src/postfx/ports/mod.rs
    src/postfx/ports/post_fx_pass.rs
    src/postfx/ports/serialization.rs
    src/postfx/ports/shader_availability.rs
    src/postfx/ports/urp_render_graph.rs
    src/postfx/post_fx_pass_registry.rs
    src/postfx/post_stack.rs
    src/postfx/rendering.rs
    src/postfx/shaders.rs
    src/postfx/ssao_pass.rs
    src/streaming.rs
    src/terrain/chunk_mesh_builder.rs
    src/terrain/error.rs
    src/terrain/height_field.rs
    src/terrain/lod.rs
    src/terrain/materials.rs
    src/terrain/mod.rs
    src/terrain/ports/material_registry.rs
    src/terrain/ports/mod.rs
    src/terrain/ports/serialization.rs
    src/terrain/terrain_lod.rs
    src/voxel/adapters/chunk.rs
    src/voxel/adapters/mesh.rs
    src/voxel/adapters/mod.rs
    src/voxel/adapters/octree.rs
    src/voxel/adapters/renderer.rs
    src/voxel/adapters/storage.rs
    src/voxel/bevy_adapter.rs
    src/voxel/chunk.rs
    src/voxel/coord.rs
    src/voxel/cubic_mesher.rs
    src/voxel/delta.rs
    src/voxel/fixtures.rs
    src/voxel/greedy_mesher.rs
    src/voxel/lod.rs
    src/voxel/material.rs
    src/voxel/material_pbr.rs
    src/voxel/mesh.rs
    src/voxel/mod.rs
    src/voxel/octree.rs
    src/voxel/ports/chunk.rs
    src/voxel/ports/material.rs
    src/voxel/ports/mesh.rs
    src/voxel/ports/mod.rs
    src/voxel/ports/octree.rs
    src/voxel/ports/renderer.rs
    src/voxel/ports/serialization.rs
    src/voxel/ports/storage.rs
    src/voxel/serial.rs
    src/voxel/shape_hints.rs
    src/voxel/sprite_voxelizer.rs
    src/voxel/world.rs
    src/voxelizer.rs
    src/water/error.rs
    src/water/gerstner_wave_bank.rs
    src/water/lod_base.rs
    src/water/mod.rs
    src/water/ports/material_registry.rs
    src/water/ports/mod.rs
    src/water/ports/serialization.rs
    src/water/rendering/fluid_mesh.rs
    src/water/rendering/mod.rs
    src/water/rendering/water_lod.rs
    src/water/rendering/water_material.rs
    src/water/rendering/water_renderer.rs
    src/water/rendering/water_shader.rs
    tests/mesher_triangle_regression.rs
    tests/perf_regression_guards.rs
    unity/postfx-shaders/BloomPass.shader
    unity/postfx-shaders/BrpACES.shader
    unity/postfx-shaders/BrpBloom.shader
    unity/postfx-shaders/ChromaticAberration.shader
    unity/postfx-shaders/ColorGradingLUT.shader
    unity/postfx-shaders/README.md
    unity/postfx-shaders/SSAOPass.shader
    unity/postfx-shaders/ScreenSpaceAO.shader
    unity/postfx-shaders/ScreenSpaceGI.shader
    unity/postfx-shaders/Vignette.shader
    unity/postfx/.github/FUNDING.yml
    unity/postfx/.github/dependabot.yml
    unity/postfx/.github/workflows/ci.yml
    unity/postfx/.github/workflows/unity-test.yml
    unity/postfx/CHANGELOG.md
    unity/postfx/CODEOWNERS
    unity/postfx/CONTRIBUTING.md
    unity/postfx/LICENSE
    unity/postfx/NuGet.config
    unity/postfx/README.md
    unity/postfx/Runtime/BloomPass.cs
    unity/postfx/Runtime/IPostFxPass.cs
    unity/postfx/Runtime/Phenotype.PostFx.asmdef
    unity/postfx/Runtime/Phenotype.PostFx.asmdef.meta
    unity/postfx/Runtime/Ports/ILutPipeline.cs
    unity/postfx/Runtime/Ports/IMaterialRegistry.cs
    unity/postfx/Runtime/Ports/IPostFxPass.cs
    unity/postfx/Runtime/Ports/ISerializationPort.cs
    unity/postfx/Runtime/Ports/IShaderAvailabilityProvider.cs
    unity/postfx/Runtime/Ports/UrpRenderGraphAdapter.cs
    unity/postfx/Runtime/PostFxPassRegistry.cs
    unity/postfx/Runtime/PostStack.cs
    unity/postfx/Runtime/SSAOPass.cs
    unity/postfx/Runtime/Shaders/BloomPass.shader
    unity/postfx/Runtime/Shaders/BrpACES.shader
    unity/postfx/Runtime/Shaders/BrpBloom.shader
    unity/postfx/Runtime/Shaders/ChromaticAberration.shader
    unity/postfx/Runtime/Shaders/ColorGradingLUT.shader
    unity/postfx/Runtime/Shaders/SSAOPass.shader
    unity/postfx/Runtime/Shaders/ScreenSpaceAO.shader
    unity/postfx/Runtime/Shaders/ScreenSpaceGI.shader
    unity/postfx/Runtime/Shaders/Vignette.shader
    unity/postfx/Runtime/phenotype-postfx-variants.shadervariants
    unity/postfx/Runtime/phenotype-postfx-variants.shadervariants.meta
    unity/postfx/SECURITY.md
    unity/postfx/STATUS.md
    unity/postfx/Taskfile.yml
    unity/postfx/audit_scorecard.json
    unity/postfx/docs/boundary/phenotype-postfx.md
    unity/postfx/docs/intent/phenotype-postfx.md
    unity/postfx/docs/security/THREAT_MODEL.md
    unity/postfx/justfile
    unity/postfx/package.json
    unity/postfx/tests/.gitignore
    unity/postfx/tests/Editor/PostFxPassRegistryTests.cs
    unity/postfx/tests/Editor/PostStackEditTests.cs
    unity/postfx/tests/Phenotype.PostFx.Tests.asmdef
    unity/postfx/tests/Phenotype.PostFx.Tests.asmdef.meta
    unity/postfx/tests/PostStackSourceTests.csproj
    unity/postfx/tests/PostStackSourceTests/PostStackSourceTests.cs
    unity/postfx/tests/PostStackVariantTests/BloomPassTests.cs
    unity/postfx/tests/PostStackVariantTests/PostStackVariantTests.csproj
    unity/postfx/tests/PostStackVariantTests/SSAOPassTests.cs
    unity/postfx/tests/PostStackVariantTests/ShaderVariantValidationTests.cs
    unity/postfx/tests/PostStackVariantTests/UnityStubs.cs
    unity/postfx/tests/benchmarks/PostStackBenchmarks.cs
    unity/postfx/tests/benchmarks/PostStackBenchmarks.csproj
    unity/postfx/tests/benchmarks/Program.cs
    unity/postfx/tests/benchmarks/UnityStubsExtra.cs
    unity/terrain/.editorconfig
    unity/terrain/.gitattributes
    unity/terrain/.github/CODEOWNERS
    unity/terrain/.github/ISSUE_TEMPLATE/bug_report.md
    unity/terrain/.github/ISSUE_TEMPLATE/config.yml
    unity/terrain/.github/ISSUE_TEMPLATE/feature_request.md
    unity/terrain/.github/dependabot.yml
    unity/terrain/.github/pull_request_template.md
    unity/terrain/.github/scorecard.yml
    unity/terrain/.github/workflows/dotnet-build.yml
    unity/terrain/.gitignore
    unity/terrain/AGENTS.md
    unity/terrain/CHANGELOG.md
    unity/terrain/CLAUDE.md
    unity/terrain/CODEOWNERS
    unity/terrain/CODE_OF_CONDUCT.md
    unity/terrain/CONTRIBUTING.md
    unity/terrain/LICENSE
    unity/terrain/NuGet.config
    unity/terrain/README.md
    unity/terrain/SECURITY.md
    unity/terrain/SHIM_README.md
    unity/terrain/STATUS.md
    unity/terrain/SUPPORT.md
    unity/terrain/Taskfile.yml
    unity/terrain/_stub/Color.cs
    unity/terrain/_stub/Stub.csproj
    unity/terrain/_stub/Vector2.cs
    unity/terrain/_stub/Vector3.cs
    unity/terrain/phenotype-terrain.csproj
    unity/terrain/scripts/generate-unity-stub.sh
    unity/terrain/src/ChunkMeshBuilder.cs
    unity/terrain/src/HeightField.cs
    unity/terrain/src/LodBase.cs
    unity/terrain/src/Materials/TerrainMaterial.cs
    unity/terrain/src/Materials/TerrainMaterialProperty.cs
    unity/terrain/src/Materials/TerrainMaterialPropertyType.cs
    unity/terrain/src/Ports/IMaterialRegistry.cs
    unity/terrain/src/Ports/ISerializationPort.cs
    unity/terrain/src/TerrainLod.cs
    unity/terrain/tests/ChunkMeshBuilderTests.cs
    unity/terrain/tests/HeightFieldEdgeCaseTests.cs
    unity/terrain/tests/HeightFieldTests.cs
    unity/terrain/tests/LodBaseTests.cs
    unity/terrain/tests/TerrainLodTests.cs
    unity/terrain/tests/TerrainMaterialTests.cs
    unity/terrain/tests/TerrainPortsTests.cs
    unity/terrain/tests/phenotype-terrain.tests.csproj
    unity/water/.editorconfig
    unity/water/.gitattributes
    unity/water/.github/ISSUE_TEMPLATE/bug_report.md
    unity/water/.github/ISSUE_TEMPLATE/config.yml
    unity/water/.github/ISSUE_TEMPLATE/feature_request.md
    unity/water/.github/dependabot.yml
    unity/water/.github/pull_request_template.md
    unity/water/.github/scorecard.yml
    unity/water/.github/scripts/stub-unity-engine.sh
    unity/water/.github/workflows/dotnet-test.yml
    unity/water/.gitignore
    unity/water/AGENTS.md
    unity/water/CHANGELOG.md
    unity/water/CLAUDE.md
    unity/water/CODEOWNERS
    unity/water/CODE_OF_CONDUCT.md
    unity/water/CONTRIBUTING.md
    unity/water/LICENSE
    unity/water/NuGet.config
    unity/water/README.md
    unity/water/SECURITY.md
    unity/water/SHIM_README.md
    unity/water/STATUS.md
    unity/water/Taskfile.yml
    unity/water/phenotype-water.csproj
    unity/water/phenotype-water.slnx
    unity/water/src/GerstnerWaveBank.cs
    unity/water/src/Ports/IMaterialRegistry.cs
    unity/water/src/Ports/ISerializationPort.cs
    unity/water/src/Rendering/FluidMesh.cs
    unity/water/src/Rendering/WaterLod.cs
    unity/water/src/Rendering/WaterMaterial.cs
    unity/water/src/Rendering/WaterRenderer.cs
    unity/water/src/Rendering/WaterShader.cs
    unity/water/src/UnityEngineStubs.cs
    unity/water/tests/FluidMeshStressTests.cs
    unity/water/tests/FluidMeshTests.cs
    unity/water/tests/GerstnerWaveBankConstructionTests.cs
    unity/water/tests/GerstnerWaveBankEdgeCaseTests.cs
    unity/water/tests/GerstnerWaveBankSimulationTests.cs
    unity/water/tests/GerstnerWaveBankTestHelpers.cs
    unity/water/tests/WaterLodTests.cs
    unity/water/tests/WaterMaterialTests.cs
    unity/water/tests/WaterRendererTests.cs
    unity/water/tests/WaterShaderTests.cs
    unity/water/tests/phenotype-water.tests.csproj
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`
- `node_modules/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
