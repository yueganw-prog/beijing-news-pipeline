import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatsCard from "@/components/common/StatsCard.vue";

describe("StatsCard", () => {
  it("renders label and value", () => {
    const wrapper = mount(StatsCard, {
      props: { label: "文章总数", value: "1,234" },
    });
    expect(wrapper.text()).toContain("文章总数");
    expect(wrapper.text()).toContain("1,234");
  });

  it("renders subtitle when provided", () => {
    const wrapper = mount(StatsCard, {
      props: { label: "Total", value: "42", sub: "Updated 1h ago" },
    });
    expect(wrapper.text()).toContain("Updated 1h ago");
  });

  it("does not render subtitle when not provided", () => {
    const wrapper = mount(StatsCard, {
      props: { label: "Total", value: "42" },
    });
    const subEl = wrapper.find(".stat-sub");
    expect(subEl.exists()).toBe(false);
  });

  it("applies color class", () => {
    const wrapper = mount(StatsCard, {
      props: { label: "Test", value: "1", color: "blue" },
    });
    expect(wrapper.classes()).toContain("blue");
  });
});
