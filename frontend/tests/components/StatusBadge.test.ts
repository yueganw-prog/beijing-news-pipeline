import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatusBadge from "@/components/common/StatusBadge.vue";

describe("StatusBadge", () => {
  it("renders tech badge with correct class", () => {
    const wrapper = mount(StatusBadge, {
      props: { category: "tech" },
    });
    expect(wrapper.text()).toBe("科技");
    expect(wrapper.classes()).toContain("badge-tech");
  });

  it("renders finance badge", () => {
    const wrapper = mount(StatusBadge, {
      props: { category: "finance" },
    });
    expect(wrapper.text()).toBe("财经");
    expect(wrapper.classes()).toContain("badge-finance");
  });

  it("renders local badge", () => {
    const wrapper = mount(StatusBadge, {
      props: { category: "local" },
    });
    expect(wrapper.text()).toBe("本地");
    expect(wrapper.classes()).toContain("badge-local");
  });

  it("falls back to raw category string for unknown categories", () => {
    const wrapper = mount(StatusBadge, {
      props: { category: "international" },
    });
    expect(wrapper.text()).toBe("international");
  });
});
