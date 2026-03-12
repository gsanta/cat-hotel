import Page from '@/components/Page';
import { Box, Card, Heading, Image } from '@chakra-ui/react';
import mainImage from '@/assets/images/main.jpg';

const HomePage = () => {
  return (
    <Page>
      <Box display="flex" flexDirection="column" gap="6" alignItems="center" mt="8">
        <Heading size="2xl">Cicahotel</Heading>
        <Image src={mainImage} alt="Cicahotel" maxW="50rem" width="100%" borderRadius="l2" />
        <Card.Root maxW="50rem">
          <Card.Body>
            Üdvözlünk macskahotelünkben, ahol a doromboló vendégek kényelme és biztonsága az első! Szolgáltatásunk
            célja, hogy a macskák számára otthonos, játékos és teljesen biztonságos környezetet biztosítsunk, amíg
            gazdáik távol vannak. Nálunk minden cicát szeretettel, türelemmel és odafigyeléssel vár egy nyugodt,
            élménydús pihenés.
          </Card.Body>
        </Card.Root>
      </Box>
    </Page>
  );
};

export default HomePage;
