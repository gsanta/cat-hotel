import { LoginFormData } from '@/hooks/useLogin';
import { Box, Field, Separator } from '@chakra-ui/react';
import { Input } from '@/library/input';
import { UseFormRegister } from 'react-hook-form';
import { useTranslation } from 'react-i18next';

type LoginFormProps = {
  register: UseFormRegister<LoginFormData>;
};

const LoginForm = ({ register }: LoginFormProps) => {
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
      <Separator />
    </Box>
  );
};

export default LoginForm;
