import React, { useState } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, colors, shadows } from '@theme/index';

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  onClear?: () => void;
  isLoading?: boolean;
  debounceMs?: number;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search...',
  onSearch,
  onClear,
  isLoading = false,
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState('');
  const debounceTimerRef = React.useRef<NodeJS.Timeout>();

  const handleChangeText = (text: string) => {
    setQuery(text);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      onSearch(text);
    }, debounceMs);
  };

  const handleClear = () => {
    setQuery('');
    onClear?.();
    onSearch('');
  };

  React.useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  return (
    <View style={[styles.container, shadows.sm]}>
      <MaterialIcons
        name="search"
        size={20}
        color={colors.text.tertiary}
        style={styles.searchIcon}
      />

      <TextInput
        style={styles.input}
        placeholder={placeholder}
        placeholderTextColor={colors.text.tertiary}
        value={query}
        onChangeText={handleChangeText}
        editable={!isLoading}
      />

      {isLoading ? (
        <ActivityIndicator
          size="small"
          color={colors.text.secondary}
          style={styles.icon}
        />
      ) : query.length > 0 ? (
        <TouchableOpacity
          onPress={handleClear}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <MaterialIcons
            name="close"
            size={20}
            color={colors.text.secondary}
            style={styles.icon}
          />
        </TouchableOpacity>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    height: 44,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.md,
  },
  searchIcon: {
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text.primary,
    padding: 0,
  },
  icon: {
    marginLeft: spacing.sm,
  },
});
