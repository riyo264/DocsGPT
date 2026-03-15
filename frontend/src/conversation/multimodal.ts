export type ParsedMultimodalInput = {
  text: string;
  imageBase64?: string;
  imageMimeType?: string;
  isMultimodalPayload: boolean;
};

export const parseMultimodalInput = (value: string): ParsedMultimodalInput => {
  if (!value) {
    return { text: '', isMultimodalPayload: false };
  }

  const trimmed = value.trim();
  if (!trimmed.startsWith('{')) {
    return { text: value, isMultimodalPayload: false };
  }

  try {
    const parsed = JSON.parse(trimmed);
    if (typeof parsed === 'object' && parsed !== null) {
      const text = typeof parsed.text === 'string' ? parsed.text : value;
      const imageBase64 =
        typeof parsed.imageBase64 === 'string' && parsed.imageBase64.length > 0
          ? parsed.imageBase64
          : undefined;
      const imageMimeType =
        typeof parsed.imageMimeType === 'string' && parsed.imageMimeType.length > 0
          ? parsed.imageMimeType
          : undefined;

      if (imageBase64 !== undefined || text !== value) {
        return {
          text,
          imageBase64,
          imageMimeType,
          isMultimodalPayload: true,
        };
      }
    }
  } catch {
    // ignore parse errors and treat input as plain text
  }

  return { text: value, isMultimodalPayload: false };
};
