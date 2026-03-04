import GeneralError from '@/types/GeneralError';
import { api } from '@/utils/apiRoutes';
import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';

type ChangePasswordRequest = {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
};

const usePasswordChange = () => {
  return useMutation<unknown, AxiosError<GeneralError>, ChangePasswordRequest>({
    mutationFn: async (data) =>
      api.post('/api/auth/change-password/', {
        current_password: data.currentPassword,
        new_password: data.newPassword,
        new_password_confirm: data.confirmPassword,
      }),
  });
};

export default usePasswordChange;
