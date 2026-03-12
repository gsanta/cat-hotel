import { Button } from '../../button';
import { Box, Field, Separator } from '@chakra-ui/react';
import { Input } from '@/library/input';
import { UseFormRegister } from 'react-hook-form';
import { RegisterFormData } from '@/hooks/useRegister';
import { useTranslation } from 'react-i18next';

type RegistrationFormProps = {
  register: UseFormRegister<RegisterFormData>;
};

const RegistrationForm = ({ register }: RegistrationFormProps) => {
  const { t } = useTranslation();
  return (
    <Box display="flex" flexDirection="column" gap="4">
      <Field.Root>
        <Field.Label>{t('email')}</Field.Label>
        <Input variant="strong" placeholder={t('enter_your_email')} {...register('email')} />
      </Field.Root>
      <Field.Root>
        <Field.Label>{t('password')}</Field.Label>
        <Input variant="strong" placeholder={t('enter_your_password')} type="password" {...register('password')} />
      </Field.Root>
      <Field.Root>
        <Field.Label>{t('confirm_password')}</Field.Label>
        <Input
          variant="strong"
          placeholder={t('confirm_your_password')}
          type="password"
          {...register('confirmPassword')}
        />
      </Field.Root>
      <Button asChild>
        <a href="auth/google/login?from=http://localhost:3012/profile">Google</a>
      </Button>
      <Separator />
    </Box>
  );
};

export default RegistrationForm;
